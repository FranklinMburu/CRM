<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { crmService } from '../services/api'

const router = useRouter()
const route = useRoute()
const stats = ref(null)
const loading = ref(true)
const upcomingTasks = ref([])

const loadDashboard = async () => {
  try {
    const [statsData, tasksData] = await Promise.all([
      crmService.getDashboardStats(),
      crmService.getTasks()
    ])
    stats.value = statsData
    upcomingTasks.value = tasksData
      .filter(t => t.status !== 'completed')
      .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
      .slice(0, 5)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadDashboard()
})

onActivated(async () => {
  await loadDashboard()
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0)
}

const formatDate = (date) => {
  if (!date) return 'No date'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date(date))
}

const getStageColor = (stage) => {
  const colors = {
    lead: 'blue-grey',
    qualified: 'blue',
    proposal: 'purple',
    negotiation: 'orange',
    won: 'green',
    lost: 'red'
  }
  return colors[stage] || 'grey'
}

const getPriorityColor = (priority) => {
  const colors = {
    low: 'blue',
    medium: 'orange',
    high: 'red'
  }
  return colors[priority] || 'grey'
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'orange',
    in_progress: 'blue',
    completed: 'green'
  }
  return colors[status] || 'grey'
}

const navigateTo = (path) => {
  router.push(path)
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="mb-6">
          <h1 class="text-h3 font-weight-bold text-navy mb-2">Dashboard</h1>
          <p class="text-h6 text-grey-darken-1">Welcome back! Here's what's happening today.</p>
        </div>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <template v-else-if="stats">
      <!-- Stats Cards -->
      <v-row class="mb-4">
        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/contacts')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Total Contacts</p>
                <h2 class="text-h3 font-weight-bold text-navy mb-1">{{ stats.total_contacts }}</h2>
                <p class="text-caption text-grey">
                  <v-icon size="small" color="success" class="mr-1">mdi-arrow-up</v-icon>
                  View all contacts
                </p>
              </div>
              <v-avatar color="blue lighten-5" size="64">
                <v-icon size="32" color="blue">mdi-account-multiple</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/companies')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Total Companies</p>
                <h2 class="text-h3 font-weight-bold text-navy mb-1">{{ stats.total_companies }}</h2>
                <p class="text-caption text-grey">
                  <v-icon size="small" color="success" class="mr-1">mdi-arrow-up</v-icon>
                  View all companies
                </p>
              </div>
              <v-avatar color="purple lighten-5" size="64">
                <v-icon size="32" color="purple">mdi-office-building</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/deals')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Active Deals</p>
                <h2 class="text-h3 font-weight-bold text-navy mb-1">{{ stats.total_deals }}</h2>
                <p class="text-caption text-grey">
                  <v-icon size="small" color="success" class="mr-1">mdi-arrow-up</v-icon>
                  View pipeline
                </p>
              </div>
              <v-avatar color="orange lighten-5" size="64">
                <v-icon size="32" color="orange">mdi-handshake</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/deals')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Total Pipeline Value</p>
                <h2 class="text-h4 font-weight-bold text-navy mb-1">{{ formatCurrency(stats.total_deal_value) }}</h2>
                <p class="text-caption text-success font-weight-medium">
                  Won: {{ formatCurrency(stats.won_deals_value) }}
                </p>
              </div>
              <v-avatar color="green lighten-5" size="64">
                <v-icon size="32" color="green">mdi-chart-line</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Main Content Row -->
      <v-row>
        <!-- Sales Pipeline -->
        <v-col cols="12" lg="8">
          <v-card elevation="3" class="mb-4">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <div class="d-flex align-center justify-space-between w-100">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-chart-bar</v-icon>
                  <span class="text-h6 font-weight-bold">Sales Pipeline</span>
                </div>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="navigateTo('/deals')"
                >
                  View All
                  <v-icon size="small" class="ml-1">mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-4">
              <v-row>
                <v-col
                  v-for="stage in stats.deals_by_stage"
                  :key="stage.stage"
                  cols="6"
                  md="4"
                  class="mb-3"
                >
                  <div class="pipeline-stage pa-3 rounded border">
                    <div class="d-flex align-center justify-space-between mb-2">
                      <v-chip
                        :color="getStageColor(stage.stage)"
                        size="small"
                        variant="flat"
                        class="text-capitalize font-weight-bold"
                      >
                        {{ stage.stage }}
                      </v-chip>
                      <span class="text-h5 font-weight-bold">{{ stage.count }}</span>
                    </div>
                    <v-progress-linear
                      :model-value="(stage.count / stats.total_deals) * 100"
                      :color="getStageColor(stage.stage)"
                      height="6"
                      rounded
                    ></v-progress-linear>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Tasks Overview -->
          <v-card elevation="3">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <div class="d-flex align-center justify-space-between w-100">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-clipboard-check</v-icon>
                  <span class="text-h6 font-weight-bold">Upcoming Tasks</span>
                </div>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="navigateTo('/tasks')"
                >
                  View All
                  <v-icon size="small" class="ml-1">mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-0">
              <v-list v-if="upcomingTasks.length > 0" lines="two">
                <v-list-item
                  v-for="(task, index) in upcomingTasks"
                  :key="task.id"
                  class="px-4 py-3"
                  :class="{ 'bg-grey-lighten-5': index % 2 === 0 }"
                >
                  <template v-slot:prepend>
                    <v-icon
                      :color="getStatusColor(task.status)"
                      class="mr-3"
                    >
                      mdi-checkbox-marked-circle
                    </v-icon>
                  </template>

                  <v-list-item-title class="font-weight-medium mb-1">
                    {{ task.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption">
                    <v-icon size="x-small" class="mr-1">mdi-calendar</v-icon>
                    {{ formatDate(task.due_date) }}
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <div class="d-flex flex-column align-end gap-1">
                      <v-chip
                        :color="getPriorityColor(task.priority)"
                        size="x-small"
                        variant="flat"
                        class="text-capitalize"
                      >
                        {{ task.priority }}
                      </v-chip>
                      <v-chip
                        :color="getStatusColor(task.status)"
                        size="x-small"
                        variant="outlined"
                        class="text-capitalize"
                      >
                        {{ task.status.replace('_', ' ') }}
                      </v-chip>
                    </div>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="pa-8 text-center text-grey">
                <v-icon size="48" color="grey-lighten-1" class="mb-2">mdi-check-all</v-icon>
                <p>No upcoming tasks</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Sidebar -->
        <v-col cols="12" lg="4">
          <!-- Quick Actions -->
          <v-card elevation="3" class="mb-4">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <v-icon class="mr-2" color="primary">mdi-lightning-bolt</v-icon>
              <span class="text-h6 font-weight-bold">Quick Actions</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-3">
              <v-list density="compact">
                <v-list-item
                  @click="navigateTo('/contacts')"
                  class="rounded mb-2 cursor-pointer"
                  prepend-icon="mdi-account-plus"
                  title="Add New Contact"
                  subtitle="Create a new contact"
                ></v-list-item>
                <v-list-item
                  @click="navigateTo('/companies')"
                  class="rounded mb-2 cursor-pointer"
                  prepend-icon="mdi-office-building-plus"
                  title="Add New Company"
                  subtitle="Create a new company"
                ></v-list-item>
                <v-list-item
                  @click="navigateTo('/deals')"
                  class="rounded mb-2 cursor-pointer"
                  prepend-icon="mdi-handshake-outline"
                  title="Create New Deal"
                  subtitle="Start a new deal"
                ></v-list-item>
                <v-list-item
                  @click="navigateTo('/tasks')"
                  class="rounded cursor-pointer"
                  prepend-icon="mdi-plus-circle"
                  title="Add New Task"
                  subtitle="Create a new task"
                ></v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Activity Summary -->
          <v-card elevation="3">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <v-icon class="mr-2" color="primary">mdi-chart-pie</v-icon>
              <span class="text-h6 font-weight-bold">Activity Summary</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-4">
              <div class="mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-grey-darken-2">Pending Tasks</span>
                  <span class="text-h6 font-weight-bold text-orange">{{ stats.pending_tasks }}</span>
                </div>
                <v-progress-linear
                  :model-value="stats.pending_tasks > 0 ? 75 : 0"
                  color="orange"
                  height="6"
                  rounded
                ></v-progress-linear>
              </div>

              <div class="mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-grey-darken-2">Overdue Tasks</span>
                  <span class="text-h6 font-weight-bold text-red">{{ stats.overdue_tasks }}</span>
                </div>
                <v-progress-linear
                  :model-value="stats.overdue_tasks > 0 ? 60 : 0"
                  color="red"
                  height="6"
                  rounded
                ></v-progress-linear>
              </div>

              <div>
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-grey-darken-2">Win Rate</span>
                  <span class="text-h6 font-weight-bold text-green">
                    {{ stats.total_deals > 0 ? Math.round((stats.deals_by_stage.find(s => s.stage === 'won')?.count || 0) / stats.total_deals * 100) : 0 }}%
                  </span>
                </div>
                <v-progress-linear
                  :model-value="stats.total_deals > 0 ? (stats.deals_by_stage.find(s => s.stage === 'won')?.count || 0) / stats.total_deals * 100 : 0"
                  color="green"
                  height="6"
                  rounded
                ></v-progress-linear>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<style scoped>
.stat-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-left-color: rgb(var(--v-theme-primary));
}

.cursor-pointer {
  cursor: pointer;
}

.pipeline-stage {
  transition: all 0.2s ease;
}

.pipeline-stage:hover {
  background-color: rgba(0, 0, 0, 0.02);
  transform: scale(1.02);
}

.text-navy {
  color: #1a237e;
}
</style>
