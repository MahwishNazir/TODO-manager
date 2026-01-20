/**
 * JWT Token API endpoint.
 *
 * This endpoint issues JWT tokens for authenticated users to use
 * when communicating with the FastAPI backend.
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import * as jose from "jose";

// JWT configuration matching backend expectations
const JWT_ISSUER = "todo-app";
const JWT_AUDIENCE = "todo-api";
const JWT_EXPIRATION = "1h";

export async function GET(request: NextRequest) {
  try {
    // Get the current session using Better Auth
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.user) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Get the shared secret from environment
    const secret = process.env.BETTER_AUTH_SECRET;
    if (!secret) {
      console.error("BETTER_AUTH_SECRET not configured");
      return NextResponse.json(
        { error: "Server configuration error" },
        { status: 500 }
      );
    }

    // Create JWT token with claims matching backend expectations
    const secretKey = new TextEncoder().encode(secret);

    const token = await new jose.SignJWT({
      sub: session.user.id,
      email: session.user.email,
    })
      .setProtectedHeader({ alg: "HS256" })
      .setIssuedAt()
      .setIssuer(JWT_ISSUER)
      .setAudience(JWT_AUDIENCE)
      .setExpirationTime(JWT_EXPIRATION)
      .sign(secretKey);

    return NextResponse.json({
      token,
      expiresIn: 3600, // 1 hour in seconds
    });
  } catch (error) {
    console.error("Token generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate token" },
      { status: 500 }
    );
  }
}
