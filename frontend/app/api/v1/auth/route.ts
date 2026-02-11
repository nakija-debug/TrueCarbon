import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action } = body;

    if (!action) {
      return NextResponse.json(
        { error: 'action field required (login, register, or refresh)' },
        { status: 400 }
      );
    }

    let endpoint = '';
    if (action === 'login') {
      endpoint = `${FASTAPI_BASE_URL}/auth/login`;
    } else if (action === 'register') {
      endpoint = `${FASTAPI_BASE_URL}/auth/register`;
    } else if (action === 'refresh') {
      endpoint = `${FASTAPI_BASE_URL}/auth/refresh`;
    } else {
      return NextResponse.json(
        { error: 'Invalid action. Must be login, register, or refresh' },
        { status: 400 }
      );
    }

    const requestBody = { ...body };
    delete requestBody.action;

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('authorization') || '',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(errorData, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, {
      status: action === 'register' ? 201 : 200,
    });
  } catch (error) {
    console.error('Auth route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
