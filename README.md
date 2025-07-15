
# FRENT APPLICATION


# Scope
The Frent Application is designed to be a comprehensive platform that connects service providers and service seekers. It includes robust features such as user management, service listing, payments, chat, notifications, and reporting, with a strong focus on security. 

The platform will include mobile apps for Android and iOS, powered by a monolithic backend architecture and integrated with various external services like Google Maps, Stripe, Firebase, and MailChimp. The primary focus is to create a user-friendly and secure application with powerful admin tools for managing services

# Description 
The Frent Application serves as a marketplace for services, allowing users to connect with service providers, manage purchases, and interact via chat and notifications. 

The application’s admin panel will provide extensive control over user and service management, including permissions, payouts, and reporting. 

The platform ensures a high level of security with measures to prevent common attacks and incorporates multiple modules like authentication, payments, location services, and more. 

The app will be cross-platform (Flutter), with a backend built using Django and Django Rest Framework, hosted on cloud platforms like AWS or Digital Ocean.
 

---
## Tools and Technologies

| Domain           | Tools and Technologies                      |
|------------------|---------------------------------------------|
| **Backend**       | Django (Python-based framework)             |
| **API**           | Django Rest Framework (DRF)                 |
| **Mobile Apps**   | Flutter (Cross-platform for iOS and Android)|
| **Architecture**  | MVT (Monolithic Model View Template)        |
| **Server**        | AWS or Digital Ocean                        |
| **Payments**      | Stripe, Custom Withdrawals                  |
| **Maps**          | Google Maps APIs                            |
| **Push Notifications** | Firebase                               |
| **Email Services**| MailChimp                                   |

---
# Development Phases


**Total Days: 60**  
**Working Days: 49**  
**Extra Days: 11**

The development process consists of the following phases:

1. **Requirements Engineering** (7 days)
   - Project understanding, meetings, discussions, use cases, and ERD preparation.

2. **Development Iteration** (17 days total)
   - **Phase 1** (3 days): Models, database, business logic, root admin panel, and test server deployment.
   - **Phase 2** (7 days): API development.
   - **Phase 3** (3 days): Admin panel and additional API development.
   - **Phase 4** (4 days): Admin panel finalization and website development.

3. **Integrations** (7 days)
   - Integrating external services, website, modules, and various features.

4. **Testing** (7 days)
   - Documentation, code optimization, bug fixes, crowd testing, and security testing.

5. **Deployment** (7 days)
   - Deployment to production servers and app stores.

---

## Modules

### Authentication and Authorization
- Signup/Login using Phone, Email, Google, Apple, or Facebook.
- OTP Verification with 2MFA (Firebase required).
- Social account linking/delinking.
- Password management.

### Administration Portal
- Manage users, staff accounts, permissions, and services.
- Grant/revoke access to system modules.
- Full access to all system data (excluding user passwords, which are securely encrypted).

### User Management
- Two types of users: Admins (Super, Staff) and Users (Service Providers, Service Seekers).
- Users can manage profiles, favorites, and blocked accounts.

### Services Management
- Providers can add, update, and manage services.
- Buyers can purchase, cancel, refund services, and provide reviews.

### Whisperer (Notifications Module)
- Push, email, and in-app notifications (SMS optional).

### Chat Module
- Live chat, encrypted messages, and chat management.

### Reporting and Support
- Users can report accounts or services, and admins can manage reports and disable accounts.

### Payouts and Withdrawals
- Service providers can request payments via Stripe Connect or custom withdrawal methods.

### Payment Methods
- Stripe checkout handles payments with various methods like GooglePay, ApplePay, and 1Link.

### Purchases and Invoices
- Detailed purchase history and downloadable invoices for both buyers and service providers.

### Coupons and Discounts
- Admins can manage coupons and discounts.

### Location and Maps
- Google Maps integration for real-time location tracking.

### Website
- A fully responsive website with all essential pages: Home, Services, Contact, About, and more.

---

# Security Measures

The backend is protected against the following attacks:

- SQL Injection
- Cross-Site Request Forgery (CSRF)
- Cross-Site Scripting (XSS)
- Clickjacking
- Directory Traversal
- Remote Code Execution (RCE)
- Insecure Direct Object Reference (IDOR)
- Session Hijacking
- Path Traversal
- Unvalidated Redirects and Forwards

---

# HOW TO RUN

## install

```bash
git clone git@github.com:IkramKhan-DevOps/frend-neonapps.git
cd frend-neonapps
```

## initialize and run

```bash
pip install -r requirements.txt
python manage.py makemigrations core users whisper finance stripe finance order services reporting
python manage.py migrate
py manage.py runserver
```

## create superuser

```bash
python manage.py createsuperuser
```

