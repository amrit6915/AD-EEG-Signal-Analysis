import * as yup from 'yup';

export const loginSchema = yup.object({
  email: yup.string().email('Invalid email format').required('Email is required'),
  password: yup.string().min(1, 'Password is required').required('Password is required'),
});

export const registerSchema = yup.object({
  email: yup.string().email('Invalid email format').required('Email is required'),
  username: yup
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(100, 'Username too long')
    .matches(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores')
    .required('Username is required'),
  password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(/[A-Z]/, 'Must contain an uppercase letter')
    .matches(/[a-z]/, 'Must contain a lowercase letter')
    .matches(/\d/, 'Must contain a number')
    .required('Password is required'),
  full_name: yup.string().max(255).optional(),
});

export const detectionFormSchema = yup.object({
  edf_file_id: yup.string().required('Please select an EDF file'),
  seizures_file_id: yup.string().required('Please select a seizures file'),
  threshold: yup.number().min(0).max(1).required(),
});

export const profileUpdateSchema = yup.object({
  full_name: yup.string().max(255).optional(),
  email: yup.string().email('Invalid email format').optional(),
});
