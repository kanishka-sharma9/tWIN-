import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router";
import { RedirectIfSignedIn, RequireAuth } from "@/auth/guards";
import { AppShell } from "@/layouts/AppShell";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Layout } from "@/layouts/Layout";
import { Account } from "@/pages/Account";
import { Health } from "@/pages/Health";
import { Home } from "@/pages/Home";
import { Login } from "@/pages/Login";
import { SignUp } from "@/pages/SignUp";

// `import.meta.env.DEV` is false in production builds, so this route and its chunk are dropped.
const DevTokens = import.meta.env.DEV
	? lazy(() =>
			import("@/pages/DevTokens").then((m) => ({ default: m.DevTokens })),
		)
	: null;

export function App() {
	return (
		<Routes>
			<Route element={<RedirectIfSignedIn />}>
				<Route element={<AuthLayout />}>
					<Route path="/signup" element={<SignUp />} />
					<Route path="/login" element={<Login />} />
				</Route>
			</Route>
			<Route element={<RequireAuth />}>
				<Route element={<AppShell />}>
					<Route path="/" element={<Home />} />
					<Route path="/account" element={<Account />} />
				</Route>
			</Route>
			<Route element={<Layout />}>
				<Route path="/health" element={<Health />} />
				{DevTokens && (
					<Route
						path="/dev/tokens"
						element={
							<Suspense fallback={null}>
								<DevTokens />
							</Suspense>
						}
					/>
				)}
			</Route>
		</Routes>
	);
}
