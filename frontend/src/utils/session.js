export function createSessionId() {
  return `session-${Math.random().toString(36).slice(2, 11)}`;
}
