import { LoginForm } from "@/src/components/LoginForm";

export const metadata = {
  title: "Login - TODO App",
  description: "Sign in to your account",
};

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome Back
          </h1>
          <p className="text-gray-600">Sign in to access your tasks</p>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md">
          <LoginForm />
        </div>
      </div>
    </main>
  );
}
