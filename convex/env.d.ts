/**
 * The Convex runtime exposes environment variables through `process.env`
 * (configure them with `npx convex env set ...`). This ambient declaration
 * lets the functions typecheck without pulling in full Node types.
 */
declare const process: {
  env: Record<string, string | undefined>
}
