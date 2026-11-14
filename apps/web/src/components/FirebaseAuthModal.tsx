"use client";

import React, { useState } from "react";
import { usePenelopeStore } from "@/lib/store";
import {
  signInWithEmail,
  signUpWithEmail,
  signInWithGoogle,
  sendPhoneOtp,
  verifyPhoneOtp,
  signOutUser,
  AuthUser,
} from "@/lib/firebase";
import {
  Shield,
  Mail,
  Phone,
  Lock,
  User as UserIcon,
  X,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  KeyRound,
  LogOut,
} from "lucide-react";

export default function FirebaseAuthModal() {
  const { isAuthModalOpen, setAuthModalOpen, currentUser, setCurrentUser } =
    usePenelopeStore();

  const [activeTab, setActiveTab] = useState<"email" | "phone" | "demo">("email");
  const [isSignUp, setIsSignUp] = useState(false);

  // Email form state (prefilled with user's email if blank)
  const [email, setEmail] = useState("tripambiswas007@gmail.com");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("Tripam Biswas");
  const [selectedRole, setSelectedRole] = useState<AuthUser["role"]>("citizen");

  // Phone form state
  const [phone, setPhone] = useState("+91 98765 43210");
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState("123456");
  const [phoneSessionInfo, setPhoneSessionInfo] = useState("");

  // Status & feedback
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error" | "info";
    text: string;
  } | null>(null);

  if (!isAuthModalOpen) return null;

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage(null);

    try {
      if (isSignUp) {
        const user = await signUpWithEmail(email, password, displayName, selectedRole);
        setCurrentUser(user);
        setStatusMessage({
          type: "success",
          text: `Welcome, ${user.displayName}! Signed in successfully.`,
        });
      } else {
        const user = await signInWithEmail(email, password);
        setCurrentUser(user);
        setStatusMessage({
          type: "success",
          text: `Welcome back, ${user.displayName}! Authenticated via Firebase.`,
        });
      }
      setTimeout(() => setAuthModalOpen(false), 900);
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: err.message || "Authentication failed. Please verify credentials.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    setStatusMessage(null);
    try {
      const user = await signInWithGoogle(email);
      setCurrentUser(user);
      setStatusMessage({
        type: "success",
        text: `Signed in with Google as ${user.displayName} (${user.email})!`,
      });
      setTimeout(() => setAuthModalOpen(false), 900);
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: err.message || "Google Authentication failed.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSendPhoneOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage(null);

    try {
      const result = await sendPhoneOtp(phone);
      setPhoneSessionInfo(result.sessionInfo);
      setOtpSent(true);
      setStatusMessage({
        type: "info",
        text: result.message,
      });
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: err.message || "Failed to send SMS verification code.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPhoneOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage(null);

    try {
      const user = await verifyPhoneOtp(phoneSessionInfo, otpCode, phone, displayName);
      setCurrentUser(user);
      setStatusMessage({
        type: "success",
        text: `Phone verified! Signed in as ${user.displayName}.`,
      });
      setTimeout(() => setAuthModalOpen(false), 900);
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: err.message || "Invalid SMS verification code.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (roleEmail: string, roleName: string) => {
    setLoading(true);
    setStatusMessage(null);
    try {
      const user = await signInWithEmail(roleEmail, "Penelope@2026!");
      setCurrentUser(user);
      setStatusMessage({
        type: "success",
        text: `Signed in as ${roleName} (${user.role.toUpperCase()}).`,
      });
      setTimeout(() => setAuthModalOpen(false), 800);
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: err.message || "Demo login failed.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await signOutUser();
    setCurrentUser(null);
    setStatusMessage({ type: "info", text: "Signed out successfully." });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg glass-surface-3 rounded-3xl border border-white/15 p-6 md:p-8 shadow-2xl text-slate-100 overflow-hidden">
        {/* Glow Accent */}
        <div className="absolute -top-24 -right-24 w-60 h-60 bg-teal-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-60 h-60 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10 relative z-10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-teal-500/20 border border-teal-500/30 text-teal-300">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                Firebase Authentication
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                  Live
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Data today. Safer tomorrows. • Secure RBAC Access
              </p>
            </div>
          </div>
          <button
            onClick={() => setAuthModalOpen(false)}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Current User Session Bar if logged in */}
        {currentUser && (
          <div className="my-4 p-3.5 rounded-2xl bg-teal-950/40 border border-teal-500/30 flex items-center justify-between text-xs">
            <div>
              <div className="text-slate-300">
                Currently signed in as{" "}
                <span className="font-bold text-white">{currentUser.displayName}</span>
              </div>
              <div className="text-[11px] text-teal-400 flex items-center gap-1.5 mt-0.5">
                <span className="capitalize font-semibold px-2 py-0.5 rounded bg-teal-500/20">
                  {currentUser.role}
                </span>
                <span>•</span>
                <span>{currentUser.email || currentUser.phoneNumber}</span>
              </div>
            </div>
            <button
              onClick={handleSignOut}
              className="px-3 py-1.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 flex items-center gap-1.5 transition text-xs font-semibold"
            >
              <LogOut className="w-3.5 h-3.5" />
              Sign Out
            </button>
          </div>
        )}

        {/* 1-Click Google / Gmail Login Button */}
        <div className="mt-4 relative z-10">
          <button
            type="button"
            onClick={handleGoogleAuth}
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-white hover:bg-slate-100 text-slate-900 font-bold text-xs flex items-center justify-center gap-2.5 shadow-md transition"
          >
            {/* Google SVG Icon */}
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google / Gmail</span>
          </button>
        </div>

        <div className="relative my-3 flex items-center justify-center">
          <div className="border-t border-white/10 w-full" />
          <span className="bg-slate-900 px-3 text-[10px] text-slate-400 uppercase font-semibold">
            Or with Credentials
          </span>
        </div>

        {/* Method Switcher Tabs */}
        <div className="flex p-1 rounded-2xl bg-black/40 border border-white/10 mb-4 relative z-10 text-xs font-semibold">
          <button
            onClick={() => {
              setActiveTab("email");
              setStatusMessage(null);
            }}
            className={`flex-1 py-2 rounded-xl flex items-center justify-center gap-1.5 transition ${
              activeTab === "email"
                ? "bg-white/15 text-white shadow-md"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            Email Login
          </button>
          <button
            onClick={() => {
              setActiveTab("phone");
              setStatusMessage(null);
            }}
            className={`flex-1 py-2 rounded-xl flex items-center justify-center gap-1.5 transition ${
              activeTab === "phone"
                ? "bg-white/15 text-white shadow-md"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Phone className="w-3.5 h-3.5" />
            Phone (SMS OTP)
          </button>
          <button
            onClick={() => {
              setActiveTab("demo");
              setStatusMessage(null);
            }}
            className={`flex-1 py-2 rounded-xl flex items-center justify-center gap-1.5 transition ${
              activeTab === "demo"
                ? "bg-teal-500/20 text-teal-300 shadow-md border border-teal-500/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            Demo Roles
          </button>
        </div>

        {/* Feedback message banner */}
        {statusMessage && (
          <div
            className={`mb-4 p-3 rounded-2xl text-xs flex items-center gap-2 border ${
              statusMessage.type === "success"
                ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                : statusMessage.type === "error"
                ? "bg-red-500/10 text-red-300 border-red-500/30"
                : "bg-cyan-500/10 text-cyan-300 border-cyan-500/30"
            }`}
          >
            {statusMessage.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            ) : statusMessage.type === "error" ? (
              <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
            ) : (
              <KeyRound className="w-4 h-4 shrink-0 text-cyan-400" />
            )}
            <span className="leading-tight">{statusMessage.text}</span>
          </div>
        )}

        {/* TAB 1: EMAIL AUTH */}
        {activeTab === "email" && (
          <form onSubmit={handleEmailAuth} className="space-y-3.5 relative z-10">
            {isSignUp && (
              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="e.g. Tripam Biswas"
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-black/40 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-400"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-black/40 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-black/40 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-400"
                />
              </div>
            </div>

            {isSignUp && (
              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  Role
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-sm text-white focus:outline-none focus:border-teal-400"
                >
                  <option value="citizen">Citizen (Local Community)</option>
                  <option value="tourist">Tourist / Traveler</option>
                  <option value="responder">Emergency Responder (NDRF/SDRF)</option>
                  <option value="authority">Government & Disaster Authority</option>
                  <option value="ngo">NGO Relief Coordinator</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/25 hover:opacity-95 transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <span>Authenticating with Firebase...</span>
              ) : (
                <>
                  <span>{isSignUp ? "Create Account" : "Sign In with Email"}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setStatusMessage(null);
                }}
                className="text-xs text-teal-400 hover:text-teal-300 underline font-medium"
              >
                {isSignUp
                  ? "Already have an account? Sign in here"
                  : "New to PENELOPE? Create an account"}
              </button>
            </div>
          </form>
        )}

        {/* TAB 2: PHONE (SMS OTP) AUTH */}
        {activeTab === "phone" && (
          <div className="space-y-4 relative z-10">
            {!otpSent ? (
              <form onSubmit={handleSendPhoneOtp} className="space-y-3.5">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    Mobile Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="tel"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full pl-9 pr-3 py-2 rounded-xl bg-black/40 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-400 font-mono"
                    />
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    An SMS verification code will be sent to this number.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/25 hover:opacity-95 transition flex items-center justify-center gap-2"
                >
                  {loading ? "Sending SMS via Firebase..." : "Send Verification Code"}
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>
            ) : (
              <form onSubmit={handleVerifyPhoneOtp} className="space-y-3.5">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    6-Digit SMS Verification Code
                  </label>
                  <div className="relative">
                    <KeyRound className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="text"
                      maxLength={6}
                      required
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value)}
                      placeholder="123456"
                      className="w-full pl-9 pr-3 py-2 rounded-xl bg-black/40 border border-teal-500/40 text-center tracking-widest text-lg font-mono text-white focus:outline-none focus:border-teal-400"
                    />
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 text-center">
                    Enter code sent to <span className="text-white font-mono">{phone}</span>
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/25 hover:opacity-95 transition flex items-center justify-center gap-2"
                >
                  {loading ? "Verifying Code..." : "Verify & Sign In"}
                  <CheckCircle2 className="w-4 h-4" />
                </button>

                <div className="text-center pt-1">
                  <button
                    type="button"
                    onClick={() => setOtpSent(false)}
                    className="text-xs text-slate-400 hover:text-white"
                  >
                    Change phone number
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* TAB 3: DEMO ROLE QUICK-SWITCH */}
        {activeTab === "demo" && (
          <div className="space-y-2 relative z-10 max-h-72 overflow-y-auto pr-1">
            <p className="text-xs text-slate-400 mb-2">
              Select any pre-seeded persona to test role-based access control and authority command:
            </p>

            {[
              {
                role: "authority",
                name: "Dr. Rajeshwar Pant",
                email: "authority@penelope.org",
                org: "Uttarakhand SDMA",
                badge: "Disaster Authority",
              },
              {
                role: "responder",
                name: "Cdr. Vikram Rathore",
                email: "responder@penelope.org",
                org: "NDRF 8th Battalion",
                badge: "First Responder",
              },
              {
                role: "citizen",
                name: "Aarav Sharma",
                email: "citizen@penelope.org",
                org: "Chamoli Community Union",
                badge: "Local Citizen",
              },
              {
                role: "tourist",
                name: "Elena Rostova",
                email: "tourist@penelope.org",
                org: "Independent Trekker",
                badge: "Tourist / Trekker",
              },
              {
                role: "ngo",
                name: "Priyanka Nair",
                email: "ngo@penelope.org",
                org: "SEEDS Disaster Relief",
                badge: "NGO Relief",
              },
              {
                role: "admin",
                name: "System Administrator",
                email: "admin@penelope.org",
                org: "PENELOPE Operations",
                badge: "Admin",
              },
            ].map((persona) => (
              <button
                key={persona.email}
                type="button"
                onClick={() => handleDemoLogin(persona.email, persona.name)}
                disabled={loading}
                className="w-full p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-left flex items-center justify-between transition group"
              >
                <div>
                  <div className="text-xs font-bold text-white group-hover:text-teal-300 transition">
                    {persona.name}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {persona.email} • {persona.org}
                  </div>
                </div>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                  {persona.badge}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
