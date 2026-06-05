import React, { useEffect } from 'react';
import { Snackbar, Alert } from '@mui/material';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { removeToast } from '../../store/slices/uiSlice';

export default function ToastContainer() {
  const dispatch = useAppDispatch();
  const toasts = useAppSelector((state) => state.ui.toasts);

  return (
    <>
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open={true}
          autoHideDuration={4000}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          onClose={() => dispatch(removeToast(toast.id))}
        >
          <Alert
            severity={toast.severity}
            variant="filled"
            onClose={() => dispatch(removeToast(toast.id))}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  );
}
