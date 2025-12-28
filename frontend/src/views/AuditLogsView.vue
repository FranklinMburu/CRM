<script setup>
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { crmService } from '../services/api'

const route = useRoute()
const auditLogs = ref([])
const loading = ref(true)
const search = ref('')

const filteredLogs = computed(() => {
  if (!search.value) return auditLogs.value
  const searchLower = search.value.toLowerCase()
  return auditLogs.value.filter(log =>
    log.user_username?.toLowerCase().includes(searchLower) ||
    log.action?.toLowerCase().includes(searchLower) ||
    log.entity_type?.toLowerCase().includes(searchLower) ||
    log.ip_address?.toLowerCase().includes(searchLower)
  )
})

const headers = [
  { title: 'Timestamp', key: 'created_at', sortable: true },
  { title: 'User', key: 'user_username', sortable: true },
  { title: 'Action', key: 'action', sortable: true },
  { title: 'Entity', key: 'entity_type', sortable: true },
  { title: 'ID', key: 'entity_id', sortable: false },
  { title: 'IP Address', key: 'ip_address', sortable: false }
]

onMounted(async () => {
  await loadAuditLogs()
})

onActivated(async () => {
  await loadAuditLogs()
})

const loadAuditLogs = async () => {
  loading.value = true
  try {
    console.log('Starting to load audit logs...')
    const data = await crmService.getAuditLogs()
    console.log('Audit logs loaded:', data)
    auditLogs.value = data.results || []
    console.log('Audit logs assigned to ref, count:', auditLogs.value.length)
  } catch (error) {
    console.error('Failed to load audit logs:', error)
  } finally {
    loading.value = false
  }
}

const formatTimestamp = (iso) => {
  if (!iso) return 'N/A'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date(iso))
}

const getActionColor = (action) => {
  const colors = {
    'CREATE': 'success',
    'UPDATE': 'info',
    'DELETE': 'error',
    'READ': 'default',
    'LOGIN': 'warning'
  }
  return colors[action] || 'default'
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="mb-6">
          <h1 class="text-h3 font-weight-bold text-navy mb-2">Audit Logs</h1>
          <p class="text-h6 text-grey-darken-1">System activity trail and change history</p>
        </div>
      </v-col>
    </v-row>

    <!-- Search Toolbar -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search logs..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              />
              <div class="text-caption text-grey">
                {{ filteredLogs.length }} of {{ auditLogs.length }} entries
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <!-- Data Table -->
    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table
            :headers="headers"
            :items="filteredLogs"
            items-per-page="25"
            class="audit-table"
          >
            <!-- Timestamp Column -->
            <template v-slot:item.created_at="{ item }">
              <div class="text-caption">{{ formatTimestamp(item.created_at) }}</div>
            </template>

            <!-- User Column -->
            <template v-slot:item.user_username="{ item }">
              <v-chip size="small" variant="outlined">
                {{ item.user_username || 'Unknown' }}
              </v-chip>
            </template>

            <!-- Action Column -->
            <template v-slot:item.action="{ item }">
              <v-chip
                size="small"
                :color="getActionColor(item.action)"
                text-color="white"
              >
                {{ item.action }}
              </v-chip>
            </template>

            <!-- Entity Type Column -->
            <template v-slot:item.entity_type="{ item }">
              <div class="text-body-2">{{ item.entity_type }}</div>
            </template>

            <!-- Entity ID Column -->
            <template v-slot:item.entity_id="{ item }">
              <div class="text-body-2 text-grey">#{{ item.entity_id }}</div>
            </template>

            <!-- IP Address Column -->
            <template v-slot:item.ip_address="{ item }">
              <div class="text-caption font-mono">{{ item.ip_address || 'N/A' }}</div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.audit-table {
  font-size: 0.875rem;
}

.font-mono {
  font-family: 'Courier New', monospace;
}

:deep(.v-data-table__wrapper) {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}
</style>
