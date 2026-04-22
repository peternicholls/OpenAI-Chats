import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function copyToClipboard(text: string) {
  if (typeof navigator === "undefined" || !navigator.clipboard) {
    return
  }

  await navigator.clipboard.writeText(text)
}

export function speakText(text: string) {
  if (
    typeof window === "undefined" ||
    !("speechSynthesis" in window) ||
    !text.trim()
  ) {
    return
  }

  window.speechSynthesis.cancel()
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(text))
}
