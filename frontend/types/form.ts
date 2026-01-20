/**
 * Task creation form state
 */
export interface CreateTaskFormState {
  /** Form field values */
  values: {
    title: string;
  };

  /** Field-level errors */
  errors: {
    title?: string;
  };

  /** Whether form is being submitted */
  isSubmitting: boolean;

  /** Whether form has been submitted successfully */
  isSubmitted: boolean;

  /** Whether form values have been modified */
  isDirty: boolean;
}

/**
 * Task edit form state
 */
export interface EditTaskFormState {
  /** Original task ID being edited */
  taskId: number;

  /** Form field values */
  values: {
    title: string;
  };

  /** Field-level errors */
  errors: {
    title?: string;
  };

  /** Whether form is being submitted */
  isSubmitting: boolean;

  /** Original title for cancel/revert */
  originalTitle: string;
}

/**
 * Authentication form state (signup/signin)
 */
export interface AuthFormState {
  /** Form field values */
  values: {
    email: string;
    password: string;
    name?: string;
  };

  /** Field-level errors */
  errors: {
    email?: string;
    password?: string;
    name?: string;
    form?: string;
  };

  /** Whether form is being submitted */
  isSubmitting: boolean;
}

/**
 * Async operation state
 */
export type AsyncState = "idle" | "loading" | "success" | "error";
