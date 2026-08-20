import { NextRequest, NextResponse } from "next/server";

import { isCanonicalHostname } from "@/shared/config/site";

export function proxy(request: NextRequest) {
  const response = NextResponse.next();
  const forwardedHost = request.headers
    .get("x-forwarded-host")
    ?.split(",")[0]
    ?.trim();
  const hostname = (forwardedHost ?? request.nextUrl.hostname).split(":")[0];
  if (!isCanonicalHostname(hostname)) {
    response.headers.set("X-Robots-Tag", "noindex, nofollow, noarchive");
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
