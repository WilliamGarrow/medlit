/**
 * Lightweight activity tracking.
 * Fire-and-forget POST to backend. Non-blocking, no error handling.
 */

export function trackActivity(action: string, detail?: string) {
  fetch("/api/activity/track", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, detail }),
  }).catch(() => {}); // Silently ignore errors
}
