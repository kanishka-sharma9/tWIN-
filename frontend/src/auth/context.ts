import { createContext, useContext } from "react";
import type { TokenResponse, User } from "./session";

export type AuthState =
	| { status: "loading" }
	| { status: "signedOut" }
	| { status: "signedIn"; user: User };

export type AuthContextValue = {
	state: AuthState;
	/** Keeps the access token in memory and marks the person signed in. */
	signIn: (tokens: TokenResponse) => void;
	signOut: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
	const value = useContext(AuthContext);
	if (!value) throw new Error("useAuth must be used inside <AuthProvider>.");
	return value;
}

/** For screens that only render when signed in. */
export function useUser(): User {
	const { state } = useAuth();
	if (state.status !== "signedIn") throw new Error("Not signed in.");
	return state.user;
}
