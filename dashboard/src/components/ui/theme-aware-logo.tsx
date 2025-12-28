import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

interface ThemeAwareLogoProps {
  className?: string
  alt?: string
}

export function ThemeAwareLogo({
  className = "",
  alt = "IQX Logo"
}: ThemeAwareLogoProps) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch by waiting for client-side mount
  useEffect(() => {
    setMounted(true)
  }, [])

  // During SSR or before mount, use light logo as default
  const logoSrc = mounted && resolvedTheme === "dark"
    ? "/logo-dark.svg"
    : "/logo.svg"

  return (
    <img
      src={logoSrc}
      alt={alt}
      className={`transition-opacity duration-200 ${className}`}
    />
  )
}
