import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { username, password } = body;

    // Demo credentials
    const demoUser = {
      username: 'nakija540@gmail.com',
      password: '123456'
    };

    if (username === demoUser.username && password === demoUser.password) {
      return NextResponse.json(
        {
          access_token: 'demo_token_nakija540',
          token_type: 'bearer',
          user: {
            id: 1,
            email: demoUser.username,
            full_name: 'Demo User'
          }
        },
        { status: 200 }
      );
    }

    return NextResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
