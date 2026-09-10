import { convexAuth } from '@convex-dev/auth/server'
import { ResendOTP } from './ResendOTP'

export const { auth, signIn, signOut, store, isAuthenticated } = convexAuth({
  providers: [ResendOTP],
  callbacks: {
    /**
     * Assign roles. The very first person to sign in becomes the shop
     * admin; everyone after that starts as a customer and can be promoted
     * from the admin panel.
     */
    async afterUserCreatedOrUpdated(ctx, { userId, existingUserId }) {
      if (existingUserId) return
      const anyAdmin = await ctx.db
        .query('users')
        .filter((q) => q.eq(q.field('role'), 'admin'))
        .first()
      await ctx.db.patch(userId, { role: anyAdmin ? 'customer' : 'admin' })
    },
  },
})
