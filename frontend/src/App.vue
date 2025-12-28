<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from './services/api'

const router = useRouter()
const route = useRoute()
const drawer = ref(true)
const user = ref(null)
const rail = ref(false)

const isAuthenticated = computed(() => !!localStorage.getItem('token'))
const showLayout = computed(() => route.path !== '/login')

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  }
})

const menuItems = [
  { 
    title: 'Dashboard', 
    icon: 'mdi-view-dashboard-variant', 
    route: '/',
    description: 'Overview & insights',
    color: '#1976D2',
    gradient: 'linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)'
  },
  { 
    title: 'Contacts', 
    icon: 'mdi-account-group', 
    route: '/contacts',
    description: 'Manage contacts',
    color: '#0288D1',
    gradient: 'linear-gradient(135deg, #0288D1 0%, #01579B 100%)'
  },
  { 
    title: 'Companies', 
    icon: 'mdi-domain', 
    route: '/companies',
    description: 'Business partners',
    color: '#1976D2',
    gradient: 'linear-gradient(135deg, #1976D2 0%, #0D47A1 100%)'
  },
  { 
    title: 'Deals', 
    icon: 'mdi-handshake', 
    route: '/deals',
    description: 'Sales pipeline',
    color: '#0277BD',
    gradient: 'linear-gradient(135deg, #0277BD 0%, #01579B 100%)'
  },
  { 
    title: 'Tasks', 
    icon: 'mdi-checkbox-marked-circle', 
    route: '/tasks',
    description: 'Todo & reminders',
    color: '#0288D1',
    gradient: 'linear-gradient(135deg, #039BE5 0%, #01579B 100%)'
  },
  { 
    title: 'Audit Logs', 
    icon: 'mdi-history', 
    route: '/audit-logs',
    description: 'System activity trail',
    color: '#00897B',
    gradient: 'linear-gradient(135deg, #00897B 0%, #004D40 100%)'
  },
]

const handleLogout = async () => {
  try {
    await authService.logout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
}

const getUserInitials = () => {
  if (!user.value?.username) return 'U'
  return user.value.username.charAt(0).toUpperCase()
}

const getItemGradient = (item) => {
  return route.path === item.route ? item.gradient : 'transparent'
}
</script>

<template>
  <v-app>
    <template v-if="showLayout && isAuthenticated">
      <!-- Premium App Bar -->
      <v-app-bar 
        elevation="0" 
        class="app-bar glass-effect"
        height="80"
      >
        <div class="d-flex align-center w-100 px-4">
          <!-- Logo & Brand -->
          <div class="d-flex align-center">
            <v-btn 
              icon 
              @click="drawer = !drawer"
              class="mr-3"
              variant="text"
              size="large"
            >
              <v-icon>mdi-menu</v-icon>
            </v-btn>
            
            <div class="brand-section d-flex align-center">
              <div class="logo-wrapper">
                <v-icon size="36" class="logo-icon">mdi-office-building</v-icon>
              </div>
              <div class="ml-3 d-none d-md-block">
                <div class="text-h5 font-weight-bold brand-text">Mini CRM</div>
                <div class="text-caption text-grey-darken-1">Customer Success Platform</div>
              </div>
            </div>
          </div>
          
          <v-spacer></v-spacer>
          
          <!-- Search Bar -->
          <div class="search-wrapper mx-4 d-none d-sm-block">
            <v-text-field
              prepend-inner-icon="mdi-magnify"
              placeholder="Search contacts, deals, companies..."
              variant="solo"
              density="comfortable"
              hide-details
              flat
              class="search-field"
              bg-color="grey-lighten-4"
            >
              <template v-slot:append-inner>
                <v-chip size="x-small" class="search-shortcut">⌘K</v-chip>
              </template>
            </v-text-field>
          </div>
          
          <v-spacer></v-spacer>
          
          <!-- Actions -->
          <div class="d-flex align-center gap-2">
            <!-- Quick Add -->
            <v-menu offset-y>
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon 
                  v-bind="props"
                  class="action-btn"
                  variant="tonal"
                  color="primary"
                >
                  <v-icon>mdi-plus-circle</v-icon>
                </v-btn>
              </template>
              <v-list min-width="200">
                <v-list-subheader>Quick Add</v-list-subheader>
                <v-list-item prepend-icon="mdi-account-plus" title="New Contact" @click="router.push('/contacts')"></v-list-item>
                <v-list-item prepend-icon="mdi-office-building-plus" title="New Company" @click="router.push('/companies')"></v-list-item>
                <v-list-item prepend-icon="mdi-handshake" title="New Deal" @click="router.push('/deals')"></v-list-item>
                <v-list-item prepend-icon="mdi-plus" title="New Task" @click="router.push('/tasks')"></v-list-item>
              </v-list>
            </v-menu>
            
            <!-- Notifications -->
            <v-btn icon class="action-btn" variant="text">
              <v-badge color="error" content="3" dot offset-x="12" offset-y="12">
                <v-icon>mdi-bell</v-icon>
              </v-badge>
            </v-btn>
            
            <!-- User Menu -->
            <v-menu offset-y min-width="280">
              <template v-slot:activator="{ props }">
                <v-btn v-bind="props" variant="flat" class="user-btn px-2" rounded="lg">
                  <v-avatar color="primary" size="40" class="avatar-gradient">
                    <span class="text-white font-weight-bold">{{ getUserInitials() }}</span>
                  </v-avatar>
                  <div class="ml-3 text-left d-none d-lg-block">
                    <div class="text-body-2 font-weight-bold">{{ user?.username || 'User' }}</div>
                    <div class="text-caption text-grey">Premium Account</div>
                  </div>
                  <v-icon class="ml-2">mdi-chevron-down</v-icon>
                </v-btn>
              </template>
              <v-card class="user-menu-card">
                <v-card-text class="pa-4">
                  <div class="d-flex align-center mb-3">
                    <v-avatar color="primary" size="56" class="avatar-gradient">
                      <span class="text-white text-h5 font-weight-bold">{{ getUserInitials() }}</span>
                    </v-avatar>
                    <div class="ml-3">
                      <div class="text-h6 font-weight-bold">{{ user?.username || 'User' }}</div>
                      <div class="text-caption text-grey">{{ user?.email || '' }}</div>
                      <v-chip size="x-small" color="success" class="mt-1">Premium</v-chip>
                    </div>
                  </div>
                  <v-divider class="my-3"></v-divider>
                  <v-list density="compact" class="bg-transparent">
                    <v-list-item prepend-icon="mdi-account-circle" title="My Profile" subtitle="View your details"></v-list-item>
                    <v-list-item prepend-icon="mdi-cog" title="Settings" subtitle="Preferences"></v-list-item>
                    <v-list-item prepend-icon="mdi-help-circle" title="Help & Support" subtitle="Get assistance"></v-list-item>
                    <v-divider class="my-2"></v-divider>
                    <v-list-item 
                      @click="handleLogout"
                      prepend-icon="mdi-logout"
                      title="Sign Out"
                      class="text-error"
                    ></v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-menu>
          </div>
        </div>
      </v-app-bar>

      <!-- Premium Navigation Drawer -->
      <v-navigation-drawer
        v-model="drawer"
        :rail="rail"
        permanent
        class="navigation-drawer"
        width="280"
      >
        <div class="drawer-gradient"></div>
        
        <!-- Drawer Header -->
        <div class="drawer-header pa-4">
          <div v-if="!rail" class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <div class="nav-logo-wrapper">
                <v-icon color="white" size="28">mdi-office-building</v-icon>
              </div>
              <div class="ml-3">
                <div class="text-h6 font-weight-bold text-white">Workspace</div>
                <div class="text-caption text-white opacity-70">Team Dashboard</div>
              </div>
            </div>
          </div>
          <v-btn 
            v-else
            icon 
            size="small" 
            variant="text"
            color="white"
            @click="rail = false"
            class="mx-auto"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
          
          <v-btn 
            v-if="!rail"
            icon 
            size="small" 
            variant="text"
            color="white"
            @click="rail = true"
            class="collapse-btn"
          >
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </div>

        <v-divider class="border-opacity-25" color="white"></v-divider>

        <!-- Navigation Menu -->
        <v-list class="nav-list pa-3" nav>
          <v-list-item
            v-for="item in menuItems"
            :key="item.route"
            :to="item.route"
            :active="route.path === item.route"
            class="nav-item mb-2"
            rounded="xl"
            :style="{ background: getItemGradient(item) }"
          >
            <template v-slot:prepend>
              <div class="nav-icon-wrapper" :style="{ background: route.path === item.route ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.15)' }">
                <v-icon 
                  :color="route.path === item.route ? 'white' : 'white'"
                  size="22"
                >
                  {{ item.icon }}
                </v-icon>
              </div>
            </template>
            
            <v-list-item-title 
              class="font-weight-medium"
              :class="route.path === item.route ? 'text-white' : 'text-white'"
            >
              {{ item.title }}
            </v-list-item-title>
            
            <v-list-item-subtitle 
              v-if="!rail"
              :class="route.path === item.route ? 'text-white opacity-90' : 'text-white opacity-70'"
            >
              {{ item.description }}
            </v-list-item-subtitle>
            
            <template v-slot:append v-if="route.path === item.route && !rail">
              <v-icon color="white" size="20">mdi-chevron-right</v-icon>
            </template>
          </v-list-item>
        </v-list>

        <!-- Bottom Section - Help Only -->
        <template v-slot:append v-if="!rail">
          <div class="pa-4">
            <!-- Help Card -->
            <v-card variant="outlined" class="help-card" rounded="lg">
              <v-card-text class="pa-4 text-center">
                <v-avatar color="white" size="48" class="mb-3">
                  <v-icon color="primary" size="28">mdi-help-circle</v-icon>
                </v-avatar>
                <div class="text-h6 font-weight-bold text-white mb-1">Need Help?</div>
                <div class="text-caption text-white opacity-80 mb-3">Get support from our team</div>
                <v-btn size="small" variant="flat" color="white" block rounded="lg">
                  <span class="text-primary font-weight-bold">Contact Support</span>
                </v-btn>
              </v-card-text>
            </v-card>
          </div>
        </template>
      </v-navigation-drawer>
    </template>

    <!-- Main Content -->
    <v-main class="main-content">
      <router-view :key="$route.fullPath" />
    </v-main>
  </v-app>
</template>

<style scoped>
/* App Bar Styles */
.app-bar {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}

.glass-effect {
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1) !important;
}

.brand-section {
  position: relative;
}

.logo-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(21, 101, 192, 0.4);
}

.logo-icon {
  color: white;
}

.brand-text {
  background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-wrapper {
  max-width: 500px;
  width: 100%;
}

.search-field {
  border-radius: 16px !important;
  overflow: hidden;
}

.search-field :deep(.v-field) {
  border-radius: 16px;
  box-shadow: none !important;
}

.search-shortcut {
  background: rgba(0, 0, 0, 0.05);
  font-size: 10px;
  font-weight: 600;
  padding: 0 6px;
  height: 20px;
}

.action-btn {
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.user-btn {
  background: rgba(0, 0, 0, 0.02) !important;
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.user-btn:hover {
  background: rgba(0, 0, 0, 0.04) !important;
  transform: translateY(-1px);
}

.avatar-gradient {
  background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%) !important;
  box-shadow: 0 4px 12px rgba(21, 101, 192, 0.3);
}

.user-menu-card {
  border-radius: 16px !important;
  overflow: hidden;
}

/* Navigation Drawer Styles */
.navigation-drawer {
  background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%) !important;
  border-right: none !important;
  position: relative;
  overflow: hidden;
}

.drawer-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(21, 101, 192, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(13, 71, 161, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.drawer-header {
  position: relative;
  z-index: 1;
}

.nav-logo-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.collapse-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.nav-list {
  position: relative;
  z-index: 1;
}

.nav-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.nav-item:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.25);
}

.nav-item.v-list-item--active {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

/* Help Card */
.help-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(10px);
}

.help-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

/* Main Content */
.main-content {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  min-height: 100vh;
}

/* Rail Mode Adjustments */
:deep(.v-navigation-drawer--rail) {
  .nav-item {
    justify-content: center;
  }
  
  .nav-icon-wrapper {
    margin: 0;
  }
}

/* Responsive */
@media (max-width: 960px) {
  .search-wrapper {
    max-width: 300px;
  }
}

@media (max-width: 600px) {
  .app-bar {
    height: 64px !important;
  }
  
  .logo-wrapper {
    width: 40px;
    height: 40px;
  }
}

/* Scrollbar Styling */
:deep(.v-navigation-drawer__content)::-webkit-scrollbar {
  width: 6px;
}

:deep(.v-navigation-drawer__content)::-webkit-scrollbar-track {
  background: transparent;
}

:deep(.v-navigation-drawer__content)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

:deep(.v-navigation-drawer__content)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
