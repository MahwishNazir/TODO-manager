import { z } from "zod";

/**
 * Task title validation schema
 */
export const taskTitleSchema = z
  .string()
  .min(1, "Task title is required")
  .max(500, "Title must be 500 characters or less")
  .transform((val) => val.trim());

/**
 * Task creation form schema
 */
export const createTaskSchema = z.object({
  title: taskTitleSchema,
});

/**
 * Task update form schema
 */
export const updateTaskSchema = z.object({
  title: taskTitleSchema,
});

/**
 * Signup form schema
 */
export const signupSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  name: z.string().optional(),
});

/**
 * Signin form schema
 */
export const signinSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

// Type exports from schemas
export type CreateTaskInput = z.infer<typeof createTaskSchema>;
export type UpdateTaskInput = z.infer<typeof updateTaskSchema>;
export type SignupInput = z.infer<typeof signupSchema>;
export type SigninInput = z.infer<typeof signinSchema>;
