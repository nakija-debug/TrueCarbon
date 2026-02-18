import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { full_name, email, password, company_name } = body;

    // Validate input
    if (!full_name || !email || !password || !company_name) {
      return NextResponse.json(
        { detail: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Simple validation
    if (password.length < 6) {
      return NextResponse.json(
        { detail: 'Password must be at least 6 characters' },
        { status: 400 }
      );
    }

    // Store user in localStorage (simulated database)
    const user = {
      id: Math.random().toString(36).substring(7),
      full_name,
      email,
      company_name,
      created_at: new Date().toISOString()
    };

    // Return success response
    return NextResponse.json(
      {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        company_name: user.company_name,
        access_token: 'mock_token_' + user.id,
        token_type: 'bearer'
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
