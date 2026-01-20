import { RegisterForm } from "@/src/components/RegisterForm";

export const metadata = {
  title: "Register - TODO App",
  description: "Create a new account",
};

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Create Account
          </h1>
          <p className="text-gray-600">
            Register to start managing your tasks
          </p>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md">
          <RegisterForm />
        </div>
      </div>
    </main>
  );
}
