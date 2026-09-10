/* eslint-disable */
/**
 * Generated `api` utility.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import type * as ResendOTP from "../ResendOTP.js";
import type * as auth from "../auth.js";
import type * as customers from "../customers.js";
import type * as http from "../http.js";
import type * as lib_helpers from "../lib/helpers.js";
import type * as measurements from "../measurements.js";
import type * as notifications from "../notifications.js";
import type * as orders from "../orders.js";
import type * as payments from "../payments.js";
import type * as reports from "../reports.js";
import type * as seed from "../seed.js";
import type * as seedServices from "../seedServices.js";
import type * as services from "../services.js";
import type * as settings from "../settings.js";
import type * as users from "../users.js";

import type {
  ApiFromModules,
  FilterApi,
  FunctionReference,
} from "convex/server";

declare const fullApi: ApiFromModules<{
  ResendOTP: typeof ResendOTP;
  auth: typeof auth;
  customers: typeof customers;
  http: typeof http;
  "lib/helpers": typeof lib_helpers;
  measurements: typeof measurements;
  notifications: typeof notifications;
  orders: typeof orders;
  payments: typeof payments;
  reports: typeof reports;
  seed: typeof seed;
  seedServices: typeof seedServices;
  services: typeof services;
  settings: typeof settings;
  users: typeof users;
}>;

/**
 * A utility for referencing Convex functions in your app's public API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = api.myModule.myFunction;
 * ```
 */
export declare const api: FilterApi<
  typeof fullApi,
  FunctionReference<any, "public">
>;

/**
 * A utility for referencing Convex functions in your app's internal API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = internal.myModule.myFunction;
 * ```
 */
export declare const internal: FilterApi<
  typeof fullApi,
  FunctionReference<any, "internal">
>;

export declare const components: {};
