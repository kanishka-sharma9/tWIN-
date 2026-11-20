import {
	type ReactNode,
	useCallback,
	useEffect,
	useMemo,
	useState,
} from "react";
import { onLoggedOut, setAccessToken, setRefresh } from "@/api/client";
import { AuthContext, type AuthContextValue, type AuthState } from "./context";
import { endSession, refreshSession, type TokenResponse } from "./session";

/**
 * Holds who is signed in. The access token lives in memory only (D-029): on load the app asks
 * the API to exchange the refresh cookie, so a reload keeps the person signed in.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
	const [state, setState] = useState<AuthState>({ status: "loading" });

	useEffect(() => {
		setRefresh(async () => (await refreshSession()).access_token);
		const unsubscribe = onLoggedOut(() => setState({ status: "signedOut" }));
		let active = true;
		refreshSession().then(
			(tokens) => {
				if (!active) return;
				setAccessToken(tokens.access_token);
				setState({ status: "signedIn", user: tokens.user });
			},
			() => {
				if (active) setState({ status: "signedOut" });
			},
		);
		return () => {
			active = false;
			unsubscribe();
		};
	}, []);

	const signIn = useCallback((tokens: TokenResponse) => {
		setAccessToken(tokens.access_token);
		setState({ status: "signedIn", user: tokens.user });
	}, []);

	const signOut = useCallback(async () => {
		await endSession();
		setAccessToken(null);
		setState({ status: "signedOut" });
	}, []);

	const value = useMemo<AuthContextValue>(
		() => ({ state, signIn, signOut }),
		[state, signIn, signOut],
	);
	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
