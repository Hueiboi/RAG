"use client"

import { useTheme } from "next-themes"
import { Toaster as Sonner, type ToasterProps } from "sonner"
import { CircleCheckIcon, InfoIcon, TriangleAlertIcon, OctagonXIcon, Loader2Icon } from "lucide-react"

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4 text-emerald-500" />,
        info: <InfoIcon className="size-4 text-blue-500" />,
        warning: <TriangleAlertIcon className="size-4 text-amber-500" />,
        error: <OctagonXIcon className="size-4 text-destructive" />,
        loading: <Loader2Icon className="size-4 text-muted-foreground animate-spin" />,
      }}
      toastOptions={{
        classNames: {
          toast: "group toast flex items-center gap-3 w-full border p-4 rounded-xl shadow-lg bg-background text-foreground border-border",
          success: "data-[type=success]:bg-emerald-50/50 data-[type=success]:text-emerald-900 data-[type=success]:border-emerald-200 dark:data-[type=success]:bg-emerald-950/20 dark:data-[type=success]:text-emerald-200 dark:data-[type=success]:border-emerald-900/50",
          error: "data-[type=error]:bg-destructive/5 data-[type=error]:text-destructive dark:data-[type=error]:bg-destructive/10 dark:data-[type=error]:text-destructive-foreground data-[type=error]:border-destructive/20",
          warning: "data-[type=warning]:bg-amber-50/50 data-[type=warning]:text-amber-900 data-[type=warning]:border-amber-200 dark:data-[type=warning]:bg-amber-950/20 dark:data-[type=warning]:text-amber-200 dark:data-[type=warning]:border-amber-900/50",
          info: "data-[type=info]:bg-blue-50/50 data-[type=info]:text-blue-900 data-[type=info]:border-blue-200 dark:data-[type=info]:bg-blue-950/20 dark:data-[type=info]:text-blue-200 dark:data-[type=info]:border-blue-900/50",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
