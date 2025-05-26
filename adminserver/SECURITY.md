# Security Notice - Command Execution Feature

## ⚠️ Important Security Information

The Kanakku Admin MCP Server includes an `execute_command` feature that allows running system commands on your production server. While this feature includes multiple security safeguards, **it inherently carries risks** and should be used with caution.

## 🛡️ Security Safeguards Implemented

### 1. Command Whitelist
- Only pre-approved commands are allowed
- Commands must be in the `ALLOWED_COMMANDS` set
- Unknown commands are automatically blocked

### 2. Pattern-Based Blocking
- Advanced regex patterns detect dangerous operations
- Blocks destructive commands (rm, mv, chmod, etc.)
- Prevents privilege escalation (sudo, su)
- Stops file modification and network operations

### 3. Specific Command Restrictions
- **systemctl/service**: Only status queries allowed
- **find**: -exec limited to safe commands only
- **Package managers**: Query operations only
- **Command length**: Limited to 500 characters

### 4. Runtime Protection
- Automatic timeout (30 seconds default, 60 max)
- Commands wrapped with `timeout` utility
- SSH connection isolation

## 🚨 Risks and Limitations

### Inherent Risks
1. **Information Disclosure**: Commands may reveal sensitive system information
2. **Resource Consumption**: Commands could consume CPU/memory resources
3. **Log Pollution**: Commands may generate excessive log entries
4. **Bypass Attempts**: Sophisticated users might find ways to bypass restrictions

### What This Feature CANNOT Prevent
- **Social Engineering**: If someone convinces you to run malicious commands
- **Complex Exploits**: Advanced command injection techniques
- **Resource Exhaustion**: Commands that consume excessive resources within timeout
- **Information Leakage**: Accidental exposure of sensitive data in command output

## 🔒 Recommended Security Practices

### 1. SSH User Restrictions
```bash
# Create a dedicated user with minimal permissions
sudo useradd -r -s /bin/bash kanakku-admin
sudo usermod -aG adm kanakku-admin  # For log access only

# Restrict sudo access (add to /etc/sudoers.d/kanakku-admin)
kanakku-admin ALL=(ALL) NOPASSWD: /bin/systemctl status *, /bin/journalctl *
```

### 2. Network Security
- Use SSH key authentication only
- Disable password authentication
- Consider IP restrictions for SSH access
- Use non-standard SSH ports if possible

### 3. Monitoring and Auditing
- Monitor SSH access logs regularly
- Set up alerts for unusual command patterns
- Review command execution logs
- Implement log rotation and retention policies

### 4. Environment Isolation
- Use this feature only on non-critical systems when possible
- Consider using a bastion host or jump server
- Implement network segmentation
- Regular security audits

## 📋 Allowed Commands Reference

### System Information (Safe)
- `uptime`, `whoami`, `id`, `uname`, `hostname`, `date`

### Resource Monitoring (Safe)
- `free`, `df`, `du`, `top`, `htop`, `iotop`, `vmstat`, `iostat`

### Process Information (Read-Only)
- `ps`, `pgrep`, `pstree`, `jobs`

### Network Information (Read-Only)
- `netstat`, `ss`, `lsof`, `nslookup`, `dig`, `ping`, `traceroute`

### File System (Read-Only)
- `ls`, `find`, `locate`, `which`, `whereis`, `file`, `stat`

### Text Processing (Safe)
- `cat`, `head`, `tail`, `grep`, `awk`, `sed`, `sort`, `uniq`, `wc`

### Service Status (Query Only)
- `systemctl status/is-active/is-enabled/list-units/show`
- `service status`
- `journalctl` (with restrictions)

### Package Information (Query Only)
- `dpkg -l/-q`, `apt list/search/show`, `yum list/info`, `rpm -q/-i`

## 🚫 Blocked Operations

### File Modification
- `rm`, `mv`, `cp` (with redirection), `chmod`, `chown`, `mkdir`, `rmdir`

### Process Control
- `kill`, `killall`, `pkill`, `nohup`, `screen`, `tmux`

### System Control
- `reboot`, `shutdown`, `halt`, `poweroff`, `init`

### Network Operations
- `wget`, `curl` (POST/PUT/DELETE), `scp`, `rsync`, `ftp`

### Package Management
- `apt install/remove`, `yum install/remove`, `pip install`

### File Editing
- `vi`, `vim`, `nano`, `emacs`, `ed`

### Privilege Escalation
- `sudo`, `su`, `passwd`, `chsh`

### Command Chaining
- `&&`, `||`, `;`, `|` (except for safe pipes)

### File Redirection
- `>`, `>>`, `<`, `tee` (to prevent file modification)

## 🔧 Customizing Security

### Adding New Safe Commands
Edit `ALLOWED_COMMANDS` in `admin_server.py`:
```python
ALLOWED_COMMANDS.add("your_safe_command")
```

### Adding New Dangerous Patterns
Edit `DANGEROUS_PATTERNS` in `admin_server.py`:
```python
DANGEROUS_PATTERNS.append(r'\byour_dangerous_pattern\b')
```

### Disabling Command Execution
To completely disable the feature, remove the `execute_command` tool from the `handle_list_tools()` function in `admin_server.py`.

## 📞 Incident Response

If you suspect misuse of the command execution feature:

1. **Immediate Actions**:
   - Disable the MCP server
   - Check SSH access logs
   - Review command execution history
   - Check system integrity

2. **Investigation**:
   - Analyze log files for suspicious activity
   - Check for unauthorized file modifications
   - Review network connections
   - Verify system configuration

3. **Recovery**:
   - Rotate SSH keys if compromised
   - Update security configurations
   - Implement additional monitoring
   - Document lessons learned

## 📚 Additional Resources

- [SSH Security Best Practices](https://www.ssh.com/academy/ssh/security)
- [Linux Security Hardening Guide](https://linux-audit.com/linux-security-hardening-and-other-tweaks/)
- [System Monitoring with auditd](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/chap-system_auditing)

---

**Remember**: Security is a shared responsibility. While this MCP server implements multiple safeguards, the ultimate security depends on proper configuration, monitoring, and responsible usage. 