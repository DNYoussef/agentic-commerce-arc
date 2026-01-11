/**
 * Dialog Component
 * Adapted from library/components/ui/radix_dialog
 */

'use client';

import { forwardRef, createContext, useContext } from 'react';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { cn } from '@/lib/utils';
import type { ReactNode, HTMLAttributes, ButtonHTMLAttributes } from 'react';

// ============ TYPES ============

type DialogSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

interface DialogProps {
  children: ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  defaultOpen?: boolean;
  modal?: boolean;
}

interface DialogTriggerProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  asChild?: boolean;
}

interface DialogContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  size?: DialogSize;
  showCloseButton?: boolean;
  closeButtonLabel?: string;
  onClose?: () => void;
  preventCloseOnOutsideClick?: boolean;
  preventCloseOnEscape?: boolean;
}

interface DialogHeaderProps {
  children: ReactNode;
  className?: string;
}

interface DialogTitleProps {
  children: ReactNode;
  className?: string;
}

interface DialogDescriptionProps {
  children: ReactNode;
  className?: string;
}

interface DialogBodyProps {
  children: ReactNode;
  className?: string;
}

interface DialogFooterProps {
  children: ReactNode;
  className?: string;
}

interface DialogCloseProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children?: ReactNode;
  asChild?: boolean;
}

// ============ CONSTANTS ============

const DIALOG_SIZE_STYLES: Record<DialogSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-[90vw] h-[90vh]',
};

// ============ CONTEXT ============

interface DialogContextValue {
  size: DialogSize;
}

const DialogContext = createContext<DialogContextValue>({ size: 'md' });

// ============ COMPONENTS ============

export function Dialog({
  children,
  open,
  onOpenChange,
  defaultOpen,
  modal = true,
}: DialogProps) {
  return (
    <DialogPrimitive.Root
      open={open}
      onOpenChange={onOpenChange}
      defaultOpen={defaultOpen}
      modal={modal}
    >
      {children}
    </DialogPrimitive.Root>
  );
}

export const DialogTrigger = forwardRef<HTMLButtonElement, DialogTriggerProps>(
  ({ children, asChild = false, className = '', ...props }, ref) => (
    <DialogPrimitive.Trigger
      ref={ref}
      asChild={asChild}
      className={cn(
        'inline-flex items-center justify-center rounded-lg px-4 py-2',
        'bg-arc-primary text-white font-medium',
        'hover:bg-arc-secondary focus:outline-none focus:ring-2 focus:ring-arc-primary focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-colors',
        className
      )}
      {...props}
    >
      {children}
    </DialogPrimitive.Trigger>
  )
);

DialogTrigger.displayName = 'DialogTrigger';

export const DialogOverlay = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className = '', ...props }, ref) => (
    <DialogPrimitive.Overlay
      ref={ref}
      className={cn(
        'fixed inset-0 z-50 bg-black/60 backdrop-blur-sm',
        'data-[state=open]:animate-fade-in',
        className
      )}
      {...props}
    />
  )
);

DialogOverlay.displayName = 'DialogOverlay';

export const DialogContent = forwardRef<HTMLDivElement, DialogContentProps>(
  (
    {
      children,
      size = 'md',
      showCloseButton = true,
      closeButtonLabel = 'Close dialog',
      onClose,
      className = '',
      preventCloseOnOutsideClick = false,
      preventCloseOnEscape = false,
      ...props
    },
    ref
  ) => (
    <DialogPrimitive.Portal>
      <DialogOverlay />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2',
          'w-full',
          DIALOG_SIZE_STYLES[size],
          'bg-gray-900 border border-gray-700 rounded-xl shadow-xl',
          'data-[state=open]:animate-slide-up',
          'focus:outline-none',
          className
        )}
        onPointerDownOutside={(e) => {
          if (preventCloseOnOutsideClick) {
            e.preventDefault();
          }
        }}
        onEscapeKeyDown={(e) => {
          if (preventCloseOnEscape) {
            e.preventDefault();
          }
        }}
        {...props}
      >
        <DialogContext.Provider value={{ size }}>
          {children}
          {showCloseButton && (
            <DialogPrimitive.Close
              className={cn(
                'absolute right-4 top-4 rounded-full p-1.5',
                'text-gray-400 hover:text-white hover:bg-gray-800',
                'focus:outline-none focus:ring-2 focus:ring-arc-primary',
                'transition-colors'
              )}
              aria-label={closeButtonLabel}
              onClick={onClose}
            >
              <CloseIcon className="h-4 w-4" />
            </DialogPrimitive.Close>
          )}
        </DialogContext.Provider>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  )
);

DialogContent.displayName = 'DialogContent';

export function DialogHeader({ children, className = '' }: DialogHeaderProps) {
  return (
    <div className={cn('px-6 pt-6 pb-4', className)}>
      {children}
    </div>
  );
}

export const DialogTitle = forwardRef<HTMLHeadingElement, DialogTitleProps>(
  ({ children, className = '', ...props }, ref) => (
    <DialogPrimitive.Title
      ref={ref}
      className={cn('text-lg font-semibold text-white', className)}
      {...props}
    >
      {children}
    </DialogPrimitive.Title>
  )
);

DialogTitle.displayName = 'DialogTitle';

export const DialogDescription = forwardRef<HTMLParagraphElement, DialogDescriptionProps>(
  ({ children, className = '', ...props }, ref) => (
    <DialogPrimitive.Description
      ref={ref}
      className={cn('text-sm text-gray-400 mt-1', className)}
      {...props}
    >
      {children}
    </DialogPrimitive.Description>
  )
);

DialogDescription.displayName = 'DialogDescription';

export function DialogBody({ children, className = '' }: DialogBodyProps) {
  return (
    <div className={cn('px-6 py-4', className)}>
      {children}
    </div>
  );
}

export function DialogFooter({ children, className = '' }: DialogFooterProps) {
  return (
    <div
      className={cn(
        'px-6 py-4 border-t border-gray-700',
        'flex justify-end gap-3',
        className
      )}
    >
      {children}
    </div>
  );
}

export const DialogClose = forwardRef<HTMLButtonElement, DialogCloseProps>(
  ({ children, asChild = false, className = '', ...props }, ref) => (
    <DialogPrimitive.Close
      ref={ref}
      asChild={asChild}
      className={cn(
        'inline-flex items-center justify-center rounded-lg px-4 py-2',
        'bg-gray-800 text-gray-300 font-medium border border-gray-700',
        'hover:bg-gray-700 hover:text-white',
        'focus:outline-none focus:ring-2 focus:ring-arc-primary focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-colors',
        className
      )}
      {...props}
    >
      {children}
    </DialogPrimitive.Close>
  )
);

DialogClose.displayName = 'DialogClose';

// ============ ICONS ============

function CloseIcon({ className = '' }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
