<template>
  <div v-if="showModal" class="auth-modal-overlay">
    <div class="auth-modal">
      <div class="auth-modal-header">
        <h3>Идентификация пользователя</h3>
        <p class="info">Для работы с паспортами необходимо авторизироваться</p>
      </div>
      <div class="auth-modal-body">
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <input
              type="text"
              id="username"
              name="username"
              v-model="credentials.username"
              class="form-input"
              placeholder="Логин"
              autocomplete="username"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <input
              type="password"
              id="password"
              name="password"
              v-model="credentials.password"
              class="form-input"
              placeholder="Пароль"
              autocomplete="current-password"
              required
              :disabled="loading"
            >
          </div>
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          <button type="submit" style="display: none;">Войти</button>
        </form>
      </div>
      <div class="auth-modal-footer">
        <button 
          @click="handleLogin" 
          class="btn-primary"
          :disabled="loading"
        >
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
        <button 
          @click="hide" 
          class="btn-secondary"
          :disabled="loading"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from '@/assets/js/auth.js'

export default {
  name: "AuthModal",
  data() {
    return {
      showModal: false,
      credentials: {
        username: '',
        password: ''
      },
      errorMessage: '',
      loading: false,
      userName: 'неавторизован',
      isAuthenticated: false
    };
  },
  mounted() {
    console.log('AuthModal mounted, adding event listeners');
    window.addEventListener('auth-required', this.handleAuthRequired);
    window.addEventListener('check-auth', this.checkAuth);
    
    // Проверяем авторизацию при загрузке компонента
    this.checkAuth();
  },
  beforeUnmount() {
    console.log('AuthModal unmounted, removing event listeners');
    window.removeEventListener('auth-required', this.handleAuthRequired);
    window.removeEventListener('check-auth', this.checkAuth);
  },
  methods: {
    handleAuthRequired() {
      console.log('AuthModal: received auth-required event');
      this.show();
    },
    
    show() {
      console.log('AuthModal: showing modal');
      this.showModal = true;
      this.resetForm();
      this.$nextTick(() => {
        const usernameInput = document.getElementById('username');
        if (usernameInput) {
          usernameInput.focus();
        }
      });
    },
    
    hide() {
      console.log('AuthModal: hiding modal');
      this.showModal = false;
      this.resetForm();
    },
    
    resetForm() {
      this.credentials.username = '';
      this.credentials.password = '';
      this.errorMessage = '';
      this.loading = false;
    },
    
    async checkAuth() {
      console.log('AuthModal: checking authentication');
      const token = auth.getToken();
      
      if (!token) {
        console.log('AuthModal: no token found');
        this.setUserData('неавторизован', false);
        this.showAuthRequired();
        return;
      }

      try {
        const API_URL = 'http://192.168.45.248:8001/api/v1/users/whoami';
        
        const response = await fetch(API_URL, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        console.log('AuthModal: whoami status:', response.status);

        if (response.status !== 200) {
          console.log('AuthModal: whoami failed with status', response.status);
          // Очищаем невалидный токен
          auth.clearToken();
          this.setUserData('неавторизован', false);
          this.showAuthRequired();
          return;
        }

        const userData = await response.json();
        console.log('AuthModal: authentication successful', userData.username);
        this.setUserData(userData.username || 'неизвестно', true);
        
      } catch (error) {
        console.error('AuthModal: whoami request error:', error);
        this.setUserData('неавторизован', false);
        this.showAuthRequired();
      }
    },
    
    setUserData(username, authenticated) {
      this.userName = username;
      this.isAuthenticated = authenticated;
      
      console.log('AuthModal: user data updated', { username, authenticated });
      
      // Отправляем событие с данными пользователя
      window.dispatchEvent(new CustomEvent('auth-status-changed', {
        detail: {
          userName: this.userName,
          isAuthenticated: this.isAuthenticated
        }
      }));
    },
    
    showAuthRequired() {
      console.log('AuthModal: showing auth required');
      // Вызываем событие, которое обрабатывается в ToolsPassport
      window.dispatchEvent(new CustomEvent('auth-required'));
    },
    
    async handleLogin() {
      console.log('AuthModal: handling login');
      if (!this.credentials.username || !this.credentials.password) {
        this.errorMessage = 'Заполните все поля';
        return;
      }

      this.loading = true;
      this.errorMessage = '';

      try {
        const response = await fetch('http://192.168.45.248:8001/api/v1/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: this.credentials.username,
            password: this.credentials.password
          })
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          console.log('AuthModal: login successful');
          auth.setToken(data.access_token);
          this.hide();
          
          // Проверяем авторизацию после успешного логина
          await this.checkAuth();
          
          window.dispatchEvent(new CustomEvent('auth-success'));
        } else {
          console.log('AuthModal: login failed', data);
          this.errorMessage = data.detail?.[0]?.msg || 'Неверный логин или пароль';
        }
      } catch (error) {
        console.error('AuthModal: login error:', error);
        this.errorMessage = 'Ошибка подключения к серверу';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Стили остаются без изменений */
.auth-modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999 !important;
}

.auth-modal {
  background: var(--body-bcg);
  border-radius: 8px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10000 !important;
}

.auth-modal-header h3 {
  margin: 0 0 20px 0;
  color: var(--text2);
  text-align: center;
}

.auth-modal-body {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--text-bcg-6);
  border-radius: 4px;
  background: var(--tb-2);
  color: var(--text2);
  box-sizing: border-box;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: var(--button-1-bgc);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 12px;
  text-align: center;
}

.auth-modal-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.btn-primary {
  background-color: var(--button-1-bgc);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  flex: 1;
  font-size: 14px;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  flex: 1;
  font-size: 14px;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--button-1-bgc-hover);
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-primary:active:not(:disabled),
.btn-secondary:active:not(:disabled) {
  transform: translateY(1px);
}
</style>