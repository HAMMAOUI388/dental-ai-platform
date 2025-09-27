// src/app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      id: "credentials",
      name: "Clinic login",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const clinicEmail = process.env.CLINIC_USER;
        const clinicPass = process.env.CLINIC_PASS;
        if (!credentials) return null;
        if (
          credentials.email === clinicEmail &&
          credentials.password === clinicPass
        ) {
          return {
            id: "clinic-user",
            name: "Doctor",
            email: clinicEmail,
          };
        }
        return null;
      },
    }),
  ],
  pages: { signIn: "/login" },
  session: { strategy: "jwt" },
  secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };
