import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const level = searchParams.get('level');
    const alertType = searchParams.get('type');
    const limit = searchParams.get('limit') || '50';

    const queryParams = new URLSearchParams();
    if (level) queryParams.append('level', level);
    if (alertType) queryParams.append('type', alertType);
    queryParams.append('limit', limit);

    const response = await fetch(
      `${FASTAPI_BASE_URL}/alerts?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': request.headers.get('authorization') || '',
        },
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch alerts' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Alerts route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { alertId, action } = body;

    if (!alertId || !action) {
      return NextResponse.json(
        { error: 'alertId and action required' },
        { status: 400 }
      );
    }

    const endpoint =
      action === 'read'
        ? `${FASTAPI_BASE_URL}/alerts/${alertId}/read`
        : `${FASTAPI_BASE_URL}/alerts/${alertId}/dismiss`;

    const response = await fetch(endpoint, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('authorization') || '',
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `Failed to ${action} alert` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Alerts update route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
