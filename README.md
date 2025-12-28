# Novel Assistant Project

An AI-assisted system for writing novels with Python and PyQt6 interface.

## Overview

The Novel Assistant is designed to help writers create better novels through AI-powered assistance. It provides tools for generating outlines, drafting chapters, improving prose quality, and maintaining consistent voice and style throughout your work.

## Features

- **AI-Powered Writing Assistance**: Generate chapters, scenes, and character development
- **PyQt6 GUI Interface**: Full-featured writing studio with rich text editor
- **Spec-Based System**: Follows detailed specifications for consistent, high-quality output
- **Token Efficiency**: Optimized for cost-effective AI interactions
- **Multiple AI Client Support**: OpenAI and other AI services

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

```bash
# 1. Clone the repository
cd novel_assistant

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create a .env file and add your API keys:
# OPENAI_API_KEY=your_openai_key_here

# 5. Run the application
python main.py
```

## Usage

### Command Line Interface
```bash
python main.py
```

### GUI Interface
The PyQt6 interface provides a full writing studio with:
- Chapter management sidebar
- Rich text editor
- AI generation and revision tools
- Google Drive integration for saving/loading
# TypeScript check (no errors)
bun run typecheck

# Build check (should complete without errors)
bun run build

# Run tests
bun run test:e2e
```

**⚠️ DO NOT RUN `npm install`** - This project is configured for Bun. Using npm will cause dependency conflicts and Prisma errors.

### Available Scripts

```bash
# Development
bun run dev              # Start dev server with Turbopack
bun run build            # Production build
bun run start            # Start production server

# Development Tools
bun run typecheck        # TypeScript check without build
bun run lint             # ESLint + TypeScript check
bun run format           # Code formatting with Biome
bun run check            # Full check (lint + typecheck + build)

# Database
bun x prisma generate    # Generate Prisma client
bun x prisma migrate dev # Create migration
bun x prisma db push     # Push schema to database
bun x prisma studio     # Open Prisma Studio UI

# Testing
bun run test:e2e        # Run Playwright e2e tests
bun run test:e2e:ui     # Run tests in UI mode
```

## 🏛️ Architecture

- **Frontend**: Next.js 15 with App Router, TypeScript, Tailwind CSS
- **Backend**: API Routes, Prisma ORM, Supabase PostgreSQL
- **Images**: ImageKit for optimization and CDN delivery
- **Payments**: Stripe integration with secure checkout
- **Authentication**: NextAuth.js with multiple providers
- **Email**: React Email with SMTP integration
- **Deployment**: Optimized for Vercel with standalone output

## 🎯 Features Overview

### **✅ Core Marketplace Features:**

1. **Dynamic Product Catalog**
   - Real-time product management with Prisma ORM
   - Categories: Fine Art, Antique Books, Collectibles, Militaria
   - Advanced search, filtering, and sorting capabilities
   - SEO-optimized product pages with metadata
   - Related products recommendations

2. **Professional Admin Dashboard**
   - Secure authentication with role-based access
   - Multi-image upload with drag-and-drop (ImageKit integration)
   - Rich product metadata (artist, year, period, rarity, etc.)
   - Order management with status tracking
   - Analytics and reporting dashboard
   - Mobile-responsive admin interface

3. **E-commerce Functionality**
   - Shopping cart with LocalStorage persistence
   - Secure Stripe Payment Elements integration
   - Two-step checkout (Shipping → Payment)
   - Order tracking and customer accounts
   - Wishlist functionality
   - Email notifications for order updates

4. **Image Management System**
   - ImageKit CDN for fast, optimized delivery
   - Automatic resizing and format optimization
   - Multiple images per product with reordering
   - Responsive image components with Next.js
   - Advanced caching and performance optimization

5. **User Authentication & Accounts**
   - NextAuth.js with secure password hashing (bcrypt)
   - Customer registration and login flows
   - Protected routes and API endpoints
   - Account dashboard with orders and wishlist
   - Social auth providers (configurable)
   - Session management and security

6. **Email & Communication**
   - React Email with professional templates
   - Order confirmations and status updates
   - Newsletter signup functionality
   - SMTP integration (Gmail/Workspace compatible)
   - Automated notifications system

7. **Performance & SEO**
   - Server-side rendering with Next.js 15
   - TypeScript strict mode for type safety
   - Optimized bundle with code splitting
   - Comprehensive metadata and Open Graph
   - Sitemap and robots.txt generation
   - Web vitals monitoring

## 🚀 Quick Start

### **Prerequisites:**
- Node.js 18+ (v23.7.0 recommended)
- Bun package manager (or npm)
- PostgreSQL database (Supabase recommended)

### **Installation:**

```bash
# Clone the repository
git clone https://github.com/jameshorton2486/kollect-it.git
cd kollect-it

# Install dependencies
bun install

# Set up environment variables
cp .env.example .env.local
# ⚠️ Edit .env.local with your actual configuration

# Set up database
bun run db:generate
bun run db:push
bun run db:seed

# Start development server
bun run dev
```

### **Access Points:**
- **Homepage**: [http://localhost:3000](http://localhost:3000)
- **Admin Dashboard**: [http://localhost:3000/admin](http://localhost:3000/admin)
- **API Docs**: [http://localhost:3000/api/health](http://localhost:3000/api/health)

### **Default Admin Credentials:**
```
Email: admin@kollect-it.com
Password: admin123
```
**⚠️ SECURITY:** Change these credentials before production deployment!

1. **Detailed Product Pages**

- Image gallery with zoom
- Full product information
- Tabbed content (description, shipping, authentication)
- Related products carousel
- Mobile-optimized with sticky cart bar

1. **API Routes**

- RESTful API for products and categories
- Authentication-protected admin routes
- Stripe payment intent creation
- Order management endpoints
- Wishlist and cart synchronization

## 🚀 Getting Started

### **New to this project?**

👉 Start with [SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md) for a step-by-step guide!

### **Quick Start:**

```bash
cd kollect-it-marketplace

# Install dependencies
bun install

# Set up environment variables
cp .env.example .env
# ⚠️ Edit .env and add a REAL PostgreSQL DATABASE_URL (see SETUP_CHECKLIST.md)

# Set up database (first time only)
bun run db:setup

# Start the development server
bun run dev
```

Visit:

- **Homepage**: [http://localhost:3000](http://localhost:3000)
- **Admin Dashboard**: [http://localhost:3000/admin/login](http://localhost:3000/admin/login)

### **Admin Login Credentials:**

```text
Email: admin@kollect-it.com
Password: admin123
```

**⚠️ IMPORTANT:** Change these credentials before deploying to production!

### **Environment Variables:**

This project requires several API keys and configurations. See [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) for:

- Complete list of all required variables
- Where to get each API key
- How to set variables locally and on Vercel
- Security best practices

**Quick setup:**

```bash
cp .env.example .env
# Edit .env and add your API keys (see ENVIRONMENT_VARIABLES.md)
```

### **Database Setup:**

This project uses PostgreSQL. See [DATABASE_SETUP.md](./DATABASE_SETUP.md) for:

- Getting a free PostgreSQL database (Supabase, Neon, or Vercel)
- Running migrations and seeding data
- All available database commands

**Quick Database Commands:**

```bash
bun run db:setup        # Complete setup (first time)
bun run db:migrate      # Create new migration
bun run db:seed         # Seed with sample data
bun run db:studio       # Open database GUI
```

## �️ Environment Configuration

### **Required Environment Variables:**

Create a `.env.local` file with these essential configurations:

```env
# Database Connection (Supabase PostgreSQL)
DATABASE_URL="postgresql://username:password@host:port/database"

# Authentication
NEXTAUTH_SECRET="your-secure-random-string"
NEXTAUTH_URL="http://localhost:3000"

# Image Management (ImageKit CDN)
NEXT_PUBLIC_IMAGEKIT_PUBLIC_KEY="your_imagekit_public_key"
IMAGEKIT_PRIVATE_KEY="your_imagekit_private_key"
IMAGEKIT_URL_ENDPOINT="https://ik.imagekit.io/your_id/"

# Payment Processing (Stripe)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_your_stripe_key"
STRIPE_SECRET_KEY="sk_test_your_stripe_secret"
STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"

# Email Service (Optional - for notifications)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"

# Admin Configuration
ADMIN_EMAIL="admin@kollect-it.com"
ADMIN_PASSWORD="admin123"
```

### **⚠️ Security Notes:**
- Generate a strong `NEXTAUTH_SECRET`: `openssl rand -base64 32`
- Change default admin credentials before production
- Use test keys for Stripe until ready for live payments
- Keep all secrets secure and never commit them to version control

### **Service Setup Guides:**
- 📘 [Supabase Database Setup](./docs/SUPABASE_COMPLETE_SETUP.md)
- 📘 [ImageKit CDN Configuration](./docs/IMAGEKIT_SETUP.md)
- 📘 [Stripe Payment Processing](./docs/STRIPE_SETUP.md)
- 📘 [Email Notifications](./docs/EMAIL_SETUP.md)

### **Adding a New Product:**

1. Go to [http://localhost:3000/admin/login](http://localhost:3000/admin/login)
2. Sign in with the admin credentials
3. Click "**+ Add New Product**" button
4. Fill in the form:
   - **Title**: Product name
   - **Description**: Detailed description
   - **Price**: Price in dollars
   - **Category**: Select from dropdown
   - **Condition**: Fine, Very Good, Good, or Fair
   - **Year**: Production year or era (e.g., "1920", "c. 1850")
   - **Artist/Maker**: Creator name (if known)
   - **Medium/Material**: What it's made of
   - **Period/Era**: Historical period
   - **Featured**: Check to feature on homepage
5. **Upload Images**:
   - Drag and drop images onto the upload area, OR
   - Click "Browse Files" to select images
   - Upload up to 8 images per product
   - Drag images to reorder (first image is the main photo)
   - Click the delete button (X) to remove unwanted images
6. Click "**Create Product**"
7. The new product will appear on the homepage if it's one of the latest 6!

### **The Latest 6 Products Feature:**

- Products are automatically sorted by date added (newest first)
- The homepage will **ALWAYS show the 6 most recent products**
- When you add product #7, it replaces the oldest one on the homepage
- No manual updates needed! 🎉

### **Deleting Products:**

1. In the admin dashboard, scroll to the products table
2. Click "**Delete**" next to the product
3. Confirm deletion

## 🗄️ Database Structure

### **Models:**

- **User**: Admin users for authentication
- **Category**: Product categories (4 predefined)
- **Product**: Individual products with all details
- **Image**: Product images (supports multiple images per product)

### **Viewing the Database:**

```bash
cd kollect-it-dynamic
bun run db:studio
```

This opens Prisma Studio in your browser to view/edit the database directly.

## 📁 Project Structure

```text
kollect-it-dynamic/
├── prisma/
│   ├── schema.prisma       # Database schema
│   ├── seed.ts            # Initial data (categories, admin user)
│   └── dev.db             # SQLite database file
├── src/
│   ├── app/
│   │   ├── page.tsx                    # Homepage (dynamic!)
│   │   ├── admin/
│   │   │   ├── login/page.tsx         # Admin login
│   │   │   └── dashboard/page.tsx     # Admin dashboard
│   │   └── api/
│   │       ├── auth/[...nextauth]/    # Authentication
│   │       ├── products/              # Product CRUD
│   │       └── categories/            # Categories API
│   ├── components/
│   ├── lib/
│   │   ├── prisma.ts      # Database client
│   │   └── auth.ts        # Auth configuration
│   └── types/
```

## 🎨 Customization

### Design tokens and utilities

This project centralizes styling in `src/app/globals.css` and exposes a set of token-driven utilities and components to keep typography, color, spacing, and CTAs consistent across pages.

- Typography (global)
  - Headings: font-family uses `--font-serif` via base styles
  - Body text: font-family uses `--font-sans` via base styles

- Color tokens (defined on :root)
  - `--color-deep-navy`, `--color-muted-gold`, `--color-cream`, `--color-charcoal`, plus gray scales

- Utility classes (in @layer components of globals.css)
  - Text: `.text-navy`, `.text-gold`
  - Background: `.bg-cream`, `.bg-navy`
  - Border: `.border-gold`
  - Spacing: `.section-spacing` (vertical spacing for sections)
  - CTA: `.btn-cta` (uppercased, gold border/text; hover: gold bg + navy text)

Usage example:

```tsx
<section className="section-spacing bg-cream">
  <h2 className="text-4xl text-navy font-semibold mb-6">Section Title</h2>
  <p className="text-gray-700">Body copy inherits the global font and sizes.</p>
  <a className="btn-cta" href="/browse">
    Browse
  </a>
</section>
```

Guidelines:

- Do not import `globals.css` in pages/components; it is imported once by `src/app/layout.tsx`.
- Prefer token utilities over hard-coded hex values (e.g., `.text-navy` instead of `text-[#0B3D91]`).
- Keep CTAs consistent by using `.btn-cta` or equivalent Tailwind classes that reference the global tokens.
- If you need additional token utilities (e.g., `.border-navy`), add them in `globals.css` under `@layer components`.

### **Changing Colors:**

Edit `src/app/kollect-it-styles.css`:

```css
:root {
  --color-gold: #b1874c; /* Richer gold accent */
  --color-primary: #2c2c2c; /* Neutral dark for text/background */
  /* ... other colors ... */
}
```

### **Adding New Categories:**

1. Open Prisma Studio: `bun run db:studio`
2. Go to "Category" table
3. Click "Add record"
4. Fill in:
   - Name: Display name
   - Slug: URL-friendly (lowercase, hyphens)
   - Description: Category description
   - Image: Image URL

## 🚢 Production Deployment

### **Vercel Deployment (Recommended):**

✅ **Complete step-by-step guide**: [VERCEL_DEPLOYMENT_GUIDE.md](./docs/VERCEL_DEPLOYMENT_GUIDE.md)

**Quick Summary:**
1. Push code to GitHub repository
2. Connect Vercel to your GitHub account
3. Import project (auto-detects Next.js)
4. Configure environment variables in Vercel dashboard
5. Deploy with automatic HTTPS and global CDN

**Required Environment Variables for Production:**
```env
DATABASE_URL=postgresql://[supabase-connection-string]
NEXTAUTH_SECRET=[secure-random-string]
NEXTAUTH_URL=https://your-domain.vercel.app
NEXT_PUBLIC_IMAGEKIT_PUBLIC_KEY=[imagekit-public-key]
IMAGEKIT_PRIVATE_KEY=[imagekit-private-key]
STRIPE_SECRET_KEY=[stripe-live-or-test-key]
```

### **Alternative Deployment Options:**

**Netlify:**
- Configure `netlify.toml` (already included)
- Add same environment variables in Netlify dashboard
- Deploy from Git repository

**Railway/Render:**
- Configure PostgreSQL database
- Set environment variables
- Deploy with Docker or from GitHub

**Self-Hosted:**
- Use `bun run build && bun run start`
- Configure reverse proxy (nginx/Apache)
- Set up SSL certificates
- Configure database connection

---

## 🔧 Development & Customization

### **Project Structure:**
```text
src/
├── app/                          # Next.js 15 App Router
│   ├── page.tsx                 # Homepage with latest products
│   ├── products/                # Product catalog and detail pages
│   ├── cart/                    # Shopping cart management
│   ├── admin/                   # Administrative dashboard
│   └── api/                     # Backend API routes
├── components/                   # Reusable UI components
│   ├── ui/                      # Shadcn/UI component library
│   ├── forms/                   # Form components with validation
│   └── layout/                  # Header, footer, navigation
├── lib/                         # Core utilities and configurations
│   ├── auth.ts                  # NextAuth.js configuration
│   ├── prisma.ts               # Database client
│   ├── stripe.ts               # Payment processing
│   └── email.ts                # Email service configuration
├── types/                       # TypeScript type definitions
└── styles/                      # Global styles and themes
```

### **Key Features Implementation:**

**Authentication System:**
- NextAuth.js with bcrypt password hashing
- Protected routes and API endpoints
- Customer accounts with order history
- Admin authentication with role-based access

**Database Schema:**
- PostgreSQL with Prisma ORM
- Comprehensive product catalog with categories
- Order management with status tracking
- User accounts with wishlist functionality

**Payment Processing:**
- Stripe integration with secure checkout
- Webhook handling for order confirmation
- Tax calculation and shipping management
- Order tracking and customer notifications

**Image Management:**
- ImageKit CDN for optimized delivery
- Multi-image upload with drag-and-drop
- Automatic resizing and format optimization
- Gallery components with zoom functionality

### **Customization Guide:**

**Styling & Branding:**
- Edit `src/app/globals.css` for color schemes
- Update `tailwind.config.ts` for design system
- Modify components in `src/components/ui/`
- Replace logo and favicons in `public/`

**Business Logic:**
- Product categories in `prisma/schema.prisma`
- Pricing and tax logic in `src/lib/utils.ts`
- Email templates in `src/emails/`
- Admin permissions in `src/lib/auth.ts`

---

## 📊 Performance & Monitoring

### **Built-in Optimizations:**
✅ Server-side rendering for SEO and performance
✅ Image optimization with Next.js Image component
✅ Code splitting and lazy loading
✅ Static asset optimization and caching
✅ Database query optimization with Prisma
✅ CDN delivery for images and static content

### **Monitoring Setup:**
- **Vercel Analytics**: Built-in performance monitoring
- **Supabase Dashboard**: Database performance and logs
- **Stripe Dashboard**: Payment and transaction monitoring
- **ImageKit Analytics**: CDN usage and optimization metrics

### **Performance Benchmarks:**
- Homepage load time: < 2 seconds
- Product pages: < 1.5 seconds
- Image loading: < 500ms (via CDN)
- Lighthouse scores: 90+ across all metrics

---

## 🆘 Support & Maintenance

### **Getting Help:**

**Technical Issues:**
- Check [GitHub Issues](https://github.com/your-username/kollect-it-marketplace/issues)
- Review deployment logs in Vercel dashboard
- Consult service-specific documentation (Supabase, Stripe, ImageKit)

**Development Support:**
- TypeScript errors: `bun run type-check`
- Build issues: `bun run build --debug`
- Database issues: Check Supabase logs and connection
- Payment issues: Review Stripe dashboard and webhooks

### **Regular Maintenance:**

**Weekly:**
- Monitor error rates in Vercel dashboard
- Check database performance in Supabase
- Review payment processing in Stripe dashboard
- Backup critical data and configurations

**Monthly:**
- Update dependencies: `bun update`
- Review security alerts: `bun audit`
- Optimize database queries and indexes
- Analyze performance metrics and user feedback

**Quarterly:**
- Rotate API keys and secrets
- Review and update security policies
- Audit user permissions and access controls
- Plan feature updates and improvements

---

## � What's Next?

### **🚀 Ready for Enhancement:**

**Search & Discovery:**
- Advanced product search with filters
- Category-based navigation
- Product recommendations
- Search analytics and optimization

**Customer Experience:**
- Product reviews and ratings
- Wishlist sharing and social features
- Order tracking with shipping updates
- Customer support chat integration

**Business Intelligence:**
- Advanced analytics dashboard
- Sales reporting and trends
- Customer segmentation
- Inventory management alerts

**Marketing Tools:**
- Email marketing automation
- Newsletter management
- SEO optimization tools
- Social media integration

### **� Future Roadmap:**

**Advanced Features:**
- Multi-vendor marketplace support
- Subscription products and billing
- Advanced inventory management
- Mobile app with React Native

**Enterprise Features:**
- Multi-currency support
- International shipping
- Advanced tax calculations
- ERP system integration

---

## 🎉 Success Metrics

**Your Kollect-It marketplace includes:**

✅ **Professional E-Commerce Platform** - Complete shopping experience
✅ **Secure Payment Processing** - Stripe integration with PCI compliance
✅ **Content Management System** - Admin dashboard for inventory
✅ **Modern Architecture** - Next.js 15 with TypeScript and performance optimization
✅ **Production Ready** - Deployment guides and monitoring setup
✅ **Scalable Infrastructure** - CDN, database optimization, and caching
✅ **Developer Experience** - Comprehensive documentation and testing

**🌟 Congratulations! Your marketplace is ready for business.**
7. **Inventory Management**: Automatic stock updates after purchase
8. **Refund Processing**: Admin panel for Stripe refunds
9. **Shipping Integration**: Real-time shipping rates (ShipStation, EasyPost)
10. **Marketing**: Abandoned cart emails, discount codes, promotions

---

### Built with ❤️ for Kollect-It

_This is a fully functional, production-ready application. The latest 6 products feature works automatically - just add products through the admin panel and they'll appear on the homepage!_
>>>>>>> 25ce121d7267f9ca9a99ea16101cd2c911aa7c85
