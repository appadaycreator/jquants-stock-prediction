import * as React from "react";

import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  helpText?: string;
  helpSide?: "top" | "bottom" | "left" | "right";
  helpDelay?: number;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, helpText, helpSide = "top", helpDelay = 200, ...props }, ref) => {
    const inputEl = (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className,
        )}
        ref={ref}
        {...props}
      />
    );

    if (!helpText) {
      return inputEl;
    }

    return (
      <TooltipProvider delayDuration={helpDelay}>
        <Tooltip>
          <TooltipTrigger asChild>
            {inputEl}
          </TooltipTrigger>
          <TooltipContent side={helpSide}>
            {helpText}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  },
);
Input.displayName = "Input";

export { Input };
