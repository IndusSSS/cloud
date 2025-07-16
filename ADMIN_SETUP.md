# SmartSecurity Cloud - Admin User Setup Guide

## 🔐 Overview

This guide explains how to securely create and manage system administrator accounts for the SmartSecurity Cloud platform. The admin console is accessible only via HTTPS and requires proper system administrator credentials.

## 🚀 Quick Start

### 1. Initial Deployment

If you're setting up SmartSecurity Cloud for the first time:

```bash
# Clone the repository
git clone https://github.com/IndusSSS/cloud.git
cd cloud

# Run the complete deployment script
./deploy_with_admin_setup.sh
```

This script will:
- Deploy all services
- Guide you through admin user creation
- Verify the deployment

### 2. Manual Admin User Creation

If you need to create an admin user manually:

```bash
# Navigate to the project directory
cd cloud

# Run the admin creation script
python create_admin_user.py
```

## 📋 Admin User Creation Process

### Interactive Setup

The `create_admin_user.py` script provides an interactive setup:

1. **Username**: Enter a unique username (3-50 characters, alphanumeric + underscore/hyphen)
2. **Email**: Enter a valid email address
3. **Password**: Enter a strong password meeting these requirements:
   - At least 8 characters long
   - Contains uppercase and lowercase letters
   - Contains at least one number
   - Contains at least one special character
4. **Confirmation**: Confirm the password and account details

### Example Session

```bash
$ python create_admin_user.py

🔐 SmartSecurity Cloud - System Admin Creation
==================================================
This script will create a system administrator account.
This account will have full access to the admin console.

Enter admin username: admin
Enter admin email: admin@smartsecurity.solutions
Enter admin password: ********
Confirm admin password: ********

📋 Admin Account Details:
  Username: admin
  Email: admin@smartsecurity.solutions
  Password: ********

Create this admin account? (y/N): y

✅ System admin account created successfully!
   Username: admin
   Email: admin@smartsecurity.solutions
   Account Type: System Administrator
   Status: Active

🔐 You can now log in to the admin console at:
   https://admin.smartsecurity.solutions

⚠️  Please keep your credentials secure!
```

## 🔧 Admin User Management

### List Existing Admins

```bash
python create_admin_user.py --list
```

### Create Additional Admins

```bash
python create_admin_user.py
```

### Help

```bash
python create_admin_user.py --help
```

## 🔒 Security Features

### Password Requirements

- **Minimum Length**: 8 characters
- **Complexity**: Must include uppercase, lowercase, numbers, and special characters
- **Validation**: Real-time password strength checking

### Account Security

- **System Admin**: No tenant restrictions (full system access)
- **Password Hashing**: Secure bcrypt hashing
- **Audit Logging**: All admin actions are logged
- **HTTPS Only**: Admin console accessible only via HTTPS

### Access Control

- **RBAC**: Role-based access control
- **System Admin**: Full system access
- **Tenant Admin**: Tenant-scoped access
- **Regular User**: Limited access

## 🌐 Access URLs

After setup, access the admin console at:

- **Admin Console**: https://admin.smartsecurity.solutions
- **Customer Portal**: https://cloud.smartsecurity.solutions
- **API Documentation**: https://cloud.smartsecurity.solutions/api/v1/docs

## 🛠️ Troubleshooting

### Common Issues

1. **"No admin users found"**
   - Run `python create_admin_user.py` to create the first admin

2. **"Username already exists"**
   - Choose a different username or use `--list` to see existing users

3. **"Email already exists"**
   - Use a different email address

4. **"Password too weak"**
   - Ensure password meets all requirements listed above

5. **"Cannot connect to database"**
   - Ensure services are running: `docker-compose ps`
   - Check logs: `docker-compose logs -f`

### Service Management

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Start services
docker-compose up -d
```

## 📝 Admin Console Features

Once logged in, you can:

- **User Management**: Create, edit, and manage user accounts
- **Device Management**: Manage IoT devices and sensors
- **Tenant Management**: Create and manage tenant organizations
- **System Health**: Monitor system performance and health
- **Audit Logs**: View system audit trails
- **Settings**: Configure system-wide settings
- **Feature Flags**: Enable/disable system features

## 🔐 Best Practices

1. **Strong Passwords**: Use complex, unique passwords
2. **Regular Updates**: Keep admin credentials updated
3. **Limited Access**: Only grant admin access to trusted users
4. **Audit Monitoring**: Regularly review audit logs
5. **Backup Credentials**: Securely store admin credentials
6. **Multi-Factor**: Consider implementing 2FA for additional security

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review system logs: `docker-compose logs -f`
3. Verify service status: `docker-compose ps`
4. Contact the development team

## 🔄 Updates

To update the system:

```bash
# Pull latest changes
git pull origin main

# Restart services
docker-compose down
docker-compose up -d

# Verify deployment
curl -k https://localhost/api/v1/health
```

---

**⚠️ Security Note**: Keep your admin credentials secure and never share them. The admin console provides full system access and should be protected accordingly. 