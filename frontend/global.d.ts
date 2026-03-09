/** Allow dynamic import() of CSS files (side-effect only). */
declare module '*.css' {
  const content: Record<string, string>;
  export default content;
}
