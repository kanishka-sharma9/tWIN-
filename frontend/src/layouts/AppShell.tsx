import { useState } from "react";
import { Link, Outlet } from "react-router";
import { useAuth, useUser } from "@/auth/context";
import { Button } from "@/components/ui/Button";

/** The signed-in shell: a top bar and a content area. E08-S01 replaces it. */
export function AppShell() {
	const user = useUser();
	const { signOut } = useAuth();
	const [leaving, setLeaving] = useState(false);

	return (
		<div className="min-h-dvh">
			<header className="navbar bg-navbar text-navbar-foreground flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2">
				<Link
					to="/"
					className="inline-flex min-h-11 items-center text-xl font-bold"
				>
					tWIN!!
				</Link>
				<nav className="ml-auto flex min-w-0 items-center gap-3">
					<Link
						to="/account"
						className="inline-flex min-h-11 min-w-0 items-center truncate text-sm underline-offset-4 hover:underline"
					>
						<span className="truncate">{user.email}</span>
					</Link>
					<Button
						variant="outline"
						className="border-navbar-foreground/40 hover:bg-navbar-foreground hover:text-navbar"
						disabled={leaving}
						onClick={() => {
							setLeaving(true);
							void signOut();
						}}
					>
						Log out
					</Button>
				</nav>
			</header>
			<main className="mx-auto w-full max-w-3xl p-4 sm:p-8">
				<Outlet />
			</main>
		</div>
	);
}
