import { FC, PropsWithChildren } from 'react';
import styles from './index.module.scss';

// 企业级 Logo 图标
const LogoIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    <rect width="48" height="48" rx="12" fill="#2563EB"/>
    <path d="M24 12L12 18L24 24L36 18L24 12Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M12 30L24 36L36 30" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M12 24L24 30L36 24" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

// 装饰圆点
const DotsPattern = () => (
  <div className={styles.dotsPattern}>
    {[...Array(6)].map((_, i) => (
      <div key={i} className={styles.dot} style={{ animationDelay: `${i * 0.5}s` }} />
    ))}
  </div>
);

// 渐变背景
const GradientBg = () => (
  <div className={styles.gradientBg}>
    <div className={styles.gradientCircle1} />
    <div className={styles.gradientCircle2} />
  </div>
);

const AuthLayout: FC<PropsWithChildren> = ({ children }) => {
  return (
    <div className={styles.container}>
      {/* 左侧品牌区 - 企业级专业风格 */}
      <div className={styles.brandSide}>
        <GradientBg />
        <DotsPattern />
        
        <div className={styles.brandContent}>
          {/* Logo 区域 */}
          <div className={styles.brandHeader}>
            <div className={styles.logoWrapper}>
              <LogoIcon />
            </div>
            <h1 className={styles.brandName}>企业运营工作台</h1>
            <p className={styles.brandSlogan}>Enterprise Operations Workbench</p>
          </div>

          {/* 核心价值主张 */}
          <div className={styles.valueProp}>
            <h2 className={styles.valueTitle}>企业级数字化管理平台</h2>
            <p className={styles.valueDesc}>
              为企业提供高效、安全的一体化解决方案，
              助力企业实现数字化转型升级
            </p>
          </div>

          {/* 核心能力 */}
          <div className={styles.capabilities}>
            <div className={styles.capability}>
              <div className={styles.capIcon}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
              <span>全链路数字化</span>
            </div>
            <div className={styles.capability}>
              <div className={styles.capIcon}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <span>企业级安全</span>
            </div>
            <div className={styles.capability}>
              <div className={styles.capIcon}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
              </div>
              <span>多业务系统融合</span>
            </div>
          </div>

          {/* 信任指标 */}
          <div className={styles.trustBadges}>
            <div className={styles.badge}>
              <span className={styles.badgeNum}>500+</span>
              <span className={styles.badgeLabel}>企业客户</span>
            </div>
            <div className={styles.divider} />
            <div className={styles.badge}>
              <span className={styles.badgeNum}>99.9%</span>
              <span className={styles.badgeLabel}>系统可用性</span>
            </div>
            <div className={styles.divider} />
            <div className={styles.badge}>
              <span className={styles.badgeNum}>24/7</span>
              <span className={styles.badgeLabel}>技术支持</span>
            </div>
          </div>
        </div>

        {/* 版权信息 */}
        <div className={styles.brandFooter}>
          <p>© 2026 企业级多租户SaaS管理系统 Enterprise Edition</p>
        </div>
      </div>

      {/* 右侧登录区 */}
      <div className={styles.formSide}>
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;