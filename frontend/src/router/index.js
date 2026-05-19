import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('../views/LandingPage.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/LoginPage.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/RegisterPage.vue')
  },
  {
    path: '/register/cook',
    name: 'CookRegister',
    component: () => import('../views/auth/CookRegisterPage.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/auth/ForgotPasswordPage.vue')
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('../views/auth/VerifyEmailPage.vue')
  },
  {
    path: '/how-it-works',
    name: 'HowItWorks',
    component: () => import('../views/HowItWorksPage.vue')
  },
  {
    path: '/customer',
    component: () => import('../layouts/CustomerLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'CustomerDashboard',
        component: () => import('../views/customer/DashboardPage.vue')
      },
      {
        path: 'book',
        name: 'BookCook',
        component: () => import('../views/customer/BookingPage.vue')
      },
      {
        path: 'bookings',
        name: 'MyBookings',
        component: () => import('../views/customer/MyBookingsPage.vue')
      },
      {
        path: 'booking/:id',
        name: 'BookingDetail',
        component: () => import('../views/customer/BookingDetailPage.vue'),
        props: true
      },
      {
        path: 'profile',
        name: 'CustomerProfile',
        component: () => import('../views/customer/ProfilePage.vue')
      },
      {
        path: 'preferences',
        name: 'TasteProfile',
        component: () => import('../views/customer/TasteProfilePage.vue')
      }
    ]
  },
  {
    path: '/cook',
    component: () => import('../layouts/CookLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'CookDashboard',
        component: () => import('../views/cook/DashboardPage.vue')
      },
      {
        path: 'jobs',
        name: 'CookJobs',
        component: () => import('../views/cook/JobsPage.vue')
      },
      {
        path: 'earnings',
        name: 'CookEarnings',
        component: () => import('../views/cook/EarningsPage.vue')
      },
      {
        path: 'availability',
        name: 'CookAvailability',
        component: () => import('../views/cook/AvailabilityPage.vue')
      },
      {
        path: 'profile',
        name: 'CookProfile',
        component: () => import('../views/cook/ProfilePage.vue')
      }
    ]
  },
  {
    path: '/manager',
    component: () => import('../layouts/ManagerLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'ManagerDashboard',
        component: () => import('../views/manager/DashboardPage.vue')
      },
      {
        path: 'verification',
        name: 'CookVerification',
        component: () => import('../views/manager/VerificationPage.vue')
      },
      {
        path: 'complaints',
        name: 'Complaints',
        component: () => import('../views/manager/ComplaintsPage.vue')
      },
      {
        path: 'cooks',
        name: 'ManageCooks',
        component: () => import('../views/manager/CooksPage.vue')
      },
      {
        path: 'profile',
        name: 'ManagerProfile',
        component: () => import('../views/manager/ProfilePage.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/DashboardPage.vue')
      },
      {
        path: 'managers',
        name: 'ManageManagers',
        component: () => import('../views/admin/ManagersPage.vue')
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('../views/admin/AnalyticsPage.vue')
      },
      {
        path: 'policies',
        name: 'Policies',
        component: () => import('../views/admin/PoliciesPage.vue')
      },
      {
        path: 'disputes',
        name: 'Disputes',
        component: () => import('../views/admin/DisputesPage.vue')
      },
      {
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('../views/admin/ProfilePage.vue')
      }
    ]
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('../views/legal/TermsPage.vue')
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/legal/PrivacyPage.vue')
  },
  {
    path: '/cancellation-policy',
    name: 'CancellationPolicy',
    component: () => import('../views/legal/CancellationPage.vue')
  },
  {
    path: '/refund-policy',
    name: 'RefundPolicy',
    component: () => import('../views/legal/RefundPage.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) {
      return { el: to.hash, top: 80, behavior: 'smooth' }
    }
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  if (to.matched.some(r => r.meta.requiresAuth)) {
    const token = localStorage.getItem('sizzzle_token')
    if (!token || token === 'undefined' || token === 'null') return { name: 'Login', query: { redirect: to.fullPath } }

    // Role-based access control
    const userString = localStorage.getItem('sizzzle_user')
    const user = userString && userString !== 'undefined' ? JSON.parse(userString) : {}
    const role = user.role || 'customer'
    if (to.path.startsWith('/customer') && role !== 'customer') return { path: `/${role}` }
    if (to.path.startsWith('/cook') && role !== 'cook') return { path: `/${role}` }
    if (to.path.startsWith('/manager') && role !== 'manager' && role !== 'admin') return { path: `/${role}` }
    if (to.path.startsWith('/admin') && role !== 'admin') return { path: `/${role}` }
  }
  // Redirect logged-in users away from auth pages
  if (to.name === 'Login' || to.name === 'Register' || to.name === 'CookRegister' || to.name === 'ForgotPassword') {
    const token = localStorage.getItem('sizzzle_token')
    if (token && token !== 'undefined' && token !== 'null') {
      const userString = localStorage.getItem('sizzzle_user')
      const user = userString && userString !== 'undefined' ? JSON.parse(userString) : {}
      return { path: `/${user.role || 'customer'}` }
    }
  }
})

export default router
