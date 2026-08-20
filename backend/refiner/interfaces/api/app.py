from __future__ import annotations

import os
from typing import Annotated, cast

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from refiner.application.usecases.refine_resume import UploadValidationError
from refiner.core.ports import GrantNotFoundError
from refiner.infrastructure.container import Container, build_container
from refiner.interfaces.api.schemas import (
    AnalysisResponse,
    HealthResponse,
    RefinementResponse,
)


def _allowed_origins() -> list[str]:
    configured = os.getenv("REFINER_ALLOWED_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


def _container(request: Request) -> Container:
    return cast(Container, request.app.state.container)


def create_app(container: Container | None = None) -> FastAPI:
    application = FastAPI(
        title="Refiner API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )
    application.state.container = container or build_container()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Export-Token"],
    )

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    @application.post(
        "/api/v1/refinements",
        response_model=RefinementResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def refine(
        request: Request,
        resume: Annotated[UploadFile, File(description="UTF-8 .txt or .md resume")],
        job_description: Annotated[str, Form(min_length=40, max_length=20_000)],
    ) -> RefinementResponse:
        suffix = os.path.splitext(resume.filename or "")[1].casefold()
        if suffix not in {".txt", ".md"}:
            raise HTTPException(status_code=415, detail="upload a UTF-8 .txt or .md resume")
        try:
            uploaded_bytes = await resume.read(256 * 1024 + 1)
        finally:
            await resume.close()
        try:
            result = _container(request).refine_resume.execute(
                uploaded_bytes,
                job_description,
            )
        except UploadValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        analysis = result.analysis
        return RefinementResponse(
            analysis=AnalysisResponse(
                coverage_score=analysis.coverage_score,
                matched_keywords=list(analysis.matched_keywords),
                missing_keywords=list(analysis.missing_keywords),
                strengths=list(analysis.strengths),
            ),
            rewritten_resume=result.rewritten_resume,
            export_token=result.export_token,
            export_expires_in_seconds=result.export_expires_in_seconds,
        )

    @application.post("/api/v1/exports/pdf", response_class=Response)
    def export_pdf(
        request: Request,
        export_token: Annotated[str, Header(alias="X-Export-Token", min_length=32)],
    ) -> Response:
        try:
            pdf = _container(request).export_pdf.execute(export_token)
        except GrantNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail="export grant is invalid, expired, or already consumed",
            ) from exc
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="refined-resume.pdf"'},
        )

    return application


app = create_app()
