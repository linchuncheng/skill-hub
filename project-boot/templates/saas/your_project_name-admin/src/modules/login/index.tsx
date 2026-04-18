import { login } from '@/api/platform/auth';
import { getTenantById } from '@/api/platform/tenant';
import type { LoginReq } from '@/api/types/auth.schema';
import AuthLayout from '@/components/layout/AuthLayout';
import { useAuthStore } from '@/stores/authStore';
import { useTenantStore } from '@/stores/tenantStore';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Checkbox, Form, Input, message } from 'antd';
import { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './index.module.scss';

const LoginPage: FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const setAuthData = useAuthStore((state) => state.setAuthData);
  const { currentTenant, setCurrentTenant } = useTenantStore();

  const onFinish = async (values: LoginReq) => {
    setLoading(true);
    try {
      const data = await login(values);
      setAuthData({
        user: data.userInfo,
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
        permissions: data.permissions,
        menus: data.menus,
      });

      // 登录成功后，检查并缓存租户信息
      const tenantId = data.userInfo.tenantId;
      
      if (tenantId) {
        // 如果缓存中没有租户信息，或 tenantId 不匹配，则获取租户信息
        if (!currentTenant || String(currentTenant.id) !== String(tenantId)) {
          try {
            const tenant = await getTenantById(tenantId);
            setCurrentTenant({
              id: parseInt(String(tenant.id), 10),
              name: tenant.tenantName,
              code: tenant.tenantCode,
              status: tenant.status,
              logo: tenant.logo || undefined,
            });
          } catch (error) {
            console.error('获取租户信息失败:', error);
            // 获取失败不影响登录，使用默认显示
          }
        }
      }

      message.success('登录成功');
      navigate('/');
    } catch (error: any) {
      message.error(error.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className={styles.loginPanel}>
        {/* 登录头部 */}
        <div className={styles.loginHeader}>
          <h2>欢迎登录</h2>
          <p>请输入您的账号和密码以访问系统</p>
        </div>

        {/* 登录表单 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
          className={styles.loginForm}
          initialValues={{ remember: true }}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
            className={styles.formItem}
          >
            <Input
              placeholder="请输入用户名"
              prefix={<UserOutlined className={styles.inputIcon} />}
              size="large"
              className={styles.customInput}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
            className={styles.formItem}
          >
            <Input.Password
              placeholder="请输入密码"
              prefix={<LockOutlined className={styles.inputIcon} />}
              size="large"
              className={styles.customInput}
            />
          </Form.Item>

          <div className={styles.formOptions}>
            <Checkbox 
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className={styles.rememberCheckbox}
            >
              记住我
            </Checkbox>
            <a href="#" className={styles.forgotLink}>忘记密码？</a>
          </div>

          <Form.Item className={styles.submitItem}>
            <Button
              type="primary"
              htmlType="submit"
              block
              size="large"
              loading={loading}
              className={styles.loginBtn}
            >
              登 录
            </Button>
          </Form.Item>
        </Form>

        {/* 安全提示 */}
        <div className={styles.securityNotice}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <span>您的登录信息将通过加密连接传输</span>
        </div>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;
