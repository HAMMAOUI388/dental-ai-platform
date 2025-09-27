export { default } from "next-auth/middleware";

export const config = {
  matcher: ["/platform"], // protect only this route
};
