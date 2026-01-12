/**
 * Dropdown Menu Component
 * Adapted from library/components/ui/radix_dropdown
 */

'use client';

import { forwardRef } from 'react';
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { cn } from '@/lib/utils';
import type { ReactNode, HTMLAttributes, ButtonHTMLAttributes } from 'react';

// ============ TYPES ============

type MenuAlign = 'start' | 'center' | 'end';
type MenuSide = 'top' | 'right' | 'bottom' | 'left';
type ItemVariant = 'default' | 'destructive';

interface DropdownMenuProps {
  children: ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  defaultOpen?: boolean;
  modal?: boolean;
}

interface DropdownMenuTriggerProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  asChild?: boolean;
}

interface DropdownMenuContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  align?: MenuAlign;
  side?: MenuSide;
  sideOffset?: number;
  alignOffset?: number;
}

interface DropdownMenuItemProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onSelect'> {
  children: ReactNode;
  disabled?: boolean;
  variant?: ItemVariant;
  icon?: ReactNode;
  shortcut?: string;
  onSelect?: (event: Event) => void;
}

interface DropdownMenuLabelProps {
  children: ReactNode;
  inset?: boolean;
  className?: string;
}

interface DropdownMenuSeparatorProps {
  className?: string;
}

// ============ COMPONENTS ============

export function DropdownMenu({
  children,
  open,
  onOpenChange,
  defaultOpen,
  modal = true,
}: DropdownMenuProps) {
  return (
    <DropdownMenuPrimitive.Root
      open={open}
      onOpenChange={onOpenChange}
      defaultOpen={defaultOpen}
      modal={modal}
    >
      {children}
    </DropdownMenuPrimitive.Root>
  );
}

export const DropdownMenuTrigger = forwardRef<HTMLButtonElement, DropdownMenuTriggerProps>(
  ({ children, asChild = false, className = '', ...props }, ref) => (
    <DropdownMenuPrimitive.Trigger
      ref={ref}
      asChild={asChild}
      className={cn(
        'inline-flex items-center justify-center rounded-lg px-3 py-2',
        'bg-gray-800 text-white border border-gray-700',
        'hover:bg-gray-700 hover:border-gray-600',
        'focus:outline-none focus:ring-2 focus:ring-arc-primary focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-colors',
        className
      )}
      {...props}
    >
      {children}
    </DropdownMenuPrimitive.Trigger>
  )
);

DropdownMenuTrigger.displayName = 'DropdownMenuTrigger';

export const DropdownMenuContent = forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  (
    {
      children,
      align = 'center',
      side = 'bottom',
      sideOffset = 4,
      alignOffset = 0,
      className = '',
      ...props
    },
    ref
  ) => (
    <DropdownMenuPrimitive.Portal>
      <DropdownMenuPrimitive.Content
        ref={ref}
        align={align}
        side={side}
        sideOffset={sideOffset}
        alignOffset={alignOffset}
        className={cn(
          'z-50 min-w-[180px] overflow-hidden rounded-lg',
          'bg-gray-900 border border-gray-700 shadow-lg',
          'p-1',
          'data-[state=open]:animate-fade-in',
          className
        )}
        {...props}
      >
        {children}
      </DropdownMenuPrimitive.Content>
    </DropdownMenuPrimitive.Portal>
  )
);

DropdownMenuContent.displayName = 'DropdownMenuContent';

export const DropdownMenuItem = forwardRef<HTMLDivElement, DropdownMenuItemProps>(
  (
    {
      children,
      disabled = false,
      variant = 'default',
      icon,
      shortcut,
      onSelect,
      className = '',
      ...props
    },
    ref
  ) => {
    const variantStyles = {
      default: 'text-white focus:bg-gray-800',
      destructive: 'text-red-400 focus:bg-red-500/10 focus:text-red-400',
    };

    return (
      <DropdownMenuPrimitive.Item
        ref={ref}
        disabled={disabled}
        onSelect={onSelect}
        className={cn(
          'relative flex items-center gap-2 px-2 py-1.5 rounded-md',
          'text-sm cursor-pointer select-none outline-none',
          variantStyles[variant],
          'data-[disabled]:opacity-50 data-[disabled]:cursor-not-allowed',
          'transition-colors',
          className
        )}
        {...props}
      >
        {icon && <span className="flex-shrink-0 w-4 h-4">{icon}</span>}
        <span className="flex-grow">{children}</span>
        {shortcut && (
          <span className="ml-auto text-xs text-gray-500">{shortcut}</span>
        )}
      </DropdownMenuPrimitive.Item>
    );
  }
);

DropdownMenuItem.displayName = 'DropdownMenuItem';

export function DropdownMenuLabel({
  children,
  inset = false,
  className = '',
}: DropdownMenuLabelProps) {
  return (
    <DropdownMenuPrimitive.Label
      className={cn(
        'px-2 py-1.5 text-xs font-semibold text-gray-500',
        inset && 'pl-8',
        className
      )}
    >
      {children}
    </DropdownMenuPrimitive.Label>
  );
}

export function DropdownMenuSeparator({ className = '' }: DropdownMenuSeparatorProps) {
  return (
    <DropdownMenuPrimitive.Separator
      className={cn('-mx-1 my-1 h-px bg-gray-700', className)}
    />
  );
}

export function DropdownMenuGroup({ children }: { children: ReactNode }) {
  return <DropdownMenuPrimitive.Group>{children}</DropdownMenuPrimitive.Group>;
}
