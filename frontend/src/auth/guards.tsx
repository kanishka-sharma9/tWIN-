import { Navigate, Outlet } from "react-router";
import { useAuth } from "./context";

function Loading() {
	return (
		<div className="grid min-h-dvh place-items-center" aria-busy="true">
			<p role="status">Loading…</p>
		</div>
	);
}

/** Signed-out visitors go to /login. */
export function RequireAuth() {
	const { state } = useAuth();
	if (state.status === "loading") return <Loading />;
	if (state.status === "signedOut") return <Navigate to="/login" replace />;
	return <Outlet />;
}

/** Signed-in visitors skip /login and /signup. */
export function RedirectIfSignedIn() {
	const { state } = useAuth();
	if (state.status === "loading") return <Loading />;
	if (state.status === "signedIn") return <Navigate to="/" replace />;
	return <Outlet />;
}
