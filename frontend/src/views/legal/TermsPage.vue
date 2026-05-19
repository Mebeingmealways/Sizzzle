<template>
  <div class="legal-page">
    <div class="legal-container">
      <a href="#" class="legal-back" @click.prevent="$router.back()">&larr; Back</a>
      <h1>Terms of Service</h1>
      <p class="legal-updated">Last updated: January 2026</p>

      <section>
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using the Sizzzle platform ("Service"), you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.</p>
      </section>

      <section>
        <h2>2. Description of Service</h2>
        <p>Sizzzle is a platform that connects customers with home cooks for personalized meal preparation. We facilitate the booking process and provide tools for both customers and cooks to manage their interactions.</p>
      </section>

      <section>
        <h2>3. User Accounts</h2>
        <p>You must register for an account to use the Service. You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.</p>
        <ul>
          <li>You must provide accurate and complete registration information.</li>
          <li>You must be at least 18 years old to create an account.</li>
          <li>You may not share your account with others.</li>
        </ul>
      </section>

      <section>
        <h2>4. Cook Responsibilities</h2>
        <p>Cooks registered on Sizzzle agree to:</p>
        <ul>
          <li>Maintain valid food safety certifications as required by local regulations.</li>
          <li>Prepare food in hygienic conditions meeting applicable health standards.</li>
          <li>Accurately represent their skills, menus, and availability.</li>
          <li>Fulfill accepted bookings or cancel with appropriate notice.</li>
        </ul>
      </section>

      <section>
        <h2>5. Customer Responsibilities</h2>
        <p>Customers using Sizzzle agree to:</p>
        <ul>
          <li>Provide accurate booking details including dietary requirements and allergies.</li>
          <li>Be present at the confirmed location during the booking window.</li>
          <li>Treat cooks with respect and provide a safe working environment.</li>
          <li>Make timely payments for services rendered.</li>
        </ul>
      </section>

      <section>
        <h2>6. Payments &amp; Fees</h2>
        <p>All payments are processed securely through our payment partners. Sizzzle charges a platform fee which is included in the displayed pricing. Cooks receive their earnings after deducting the platform commission.</p>
      </section>

      <section>
        <h2>7. Limitation of Liability</h2>
        <p>Sizzzle acts as an intermediary platform and is not liable for the quality, safety, or outcome of meals prepared by cooks. We encourage users to communicate dietary needs and allergies clearly.</p>
      </section>

      <section>
        <h2>8. Changes to Terms</h2>
        <p>We reserve the right to modify these terms at any time. Users will be notified of significant changes via email or in-app notification.</p>
      </section>

      <section>
        <h2>9. Contact</h2>
        <p>For questions regarding these Terms, contact us at <strong>legal@sizzzle.me</strong></p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.legal-page { min-height: 100vh; background: var(--bg); padding: 40px 20px 80px; }
.legal-container { max-width: 720px; margin: 0 auto; font-family: 'Inter', sans-serif; color: var(--text); }
.legal-back { display: inline-block; margin-bottom: 24px; color: var(--primary, #2DB67D); text-decoration: none; font-weight: 600; font-size: 0.9rem; }
.legal-back:hover { text-decoration: underline; }
h1 { font-size: 2rem; font-weight: 800; margin-bottom: 4px; }
.legal-updated { font-size: 0.82rem; opacity: 0.5; margin-bottom: 32px; }
section { margin-bottom: 28px; }
h2 { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; }
p { line-height: 1.7; font-size: 0.95rem; opacity: 0.85; }
ul { padding-left: 20px; margin-top: 8px; }
li { line-height: 1.7; font-size: 0.95rem; opacity: 0.85; margin-bottom: 4px; }
</style>
