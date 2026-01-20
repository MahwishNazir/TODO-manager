import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
  footer?: {
    text: string;
    linkText: string;
    linkHref: string;
  };
}

export function AuthLayout({ children, title, description, footer }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted/50 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <h1 className="text-3xl font-bold text-primary">TaskFlow</h1>
          </Link>
        </div>
        <Card className="shadow-lg">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </CardHeader>
          <CardContent>
            {children}
            {footer && (
              <p className="mt-6 text-center text-sm text-muted-foreground">
                {footer.text}{" "}
                <Link
                  href={footer.linkHref}
                  className="font-medium text-primary hover:underline"
                >
                  {footer.linkText}
                </Link>
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
