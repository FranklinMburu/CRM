<script setup>
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { crmService } from '../services/api'

const route = useRoute()
const deals = ref([])
const companies = ref([])
const contacts = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const editedIndex = ref(-1)
const editedItem = ref({
  title: '',
  amount: 0,
  stage: 'lead',
  company: null,
  contact: null,
  expected_close_date: ''
})

const defaultItem = {
  title: '',
  amount: 0,
  stage: 'lead',
  company: null,
  contact: null,
  expected_close_date: ''
}

const stageOptions = [
  { title: 'Lead', value: 'lead' },
  { title: 'Qualified', value: 'qualified' },
  { title: 'Proposal', value: 'proposal' },
  { title: 'Negotiation', value: 'negotiation' },
  { title: 'Won', value: 'won' },
  { title: 'Lost', value: 'lost' }
]

const headers = [
  { title: 'Deal', key: 'title', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true },
  { title: 'Stage', key: 'stage', sortable: true },
  { title: 'Company', key: 'company_name', sortable: true },
  { title: 'Contact', key: 'contact_name', sortable: false },
  { title: 'Expected Close', key: 'expected_close_date', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

const filteredDeals = computed(() => {
  if (!search.value) return deals.value
  const searchLower = search.value.toLowerCase()
  return deals.value.filter(deal =>
    deal.title && deal.title.toLowerCase().includes(searchLower) ||
    deal.company_name && deal.company_name.toLowerCase().includes(searchLower) ||
    deal.contact_name && deal.contact_name.toLowerCase().includes(searchLower) ||
    deal.stage && deal.stage.toLowerCase().includes(searchLower)
  )
})

onMounted(async () => {
  await Promise.all([loadDeals(), loadCompanies(), loadContacts()])
})

onActivated(async () => {
  await Promise.all([loadDeals(), loadCompanies(), loadContacts()])
})

const loadDeals = async () => {
  loading.value = true
  try {
    const response = await crmService.getDeals()
    deals.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load deals:', error)
  } finally {
    loading.value = false
  }
}

const loadCompanies = async () => {
  try {
    const response = await crmService.getCompanies()
    companies.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load companies:', error)
  }
}

const loadContacts = async () => {
  try {
    const response = await crmService.getContacts()
    contacts.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
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

const editItem = (item) => {
  editedIndex.value = deals.value.indexOf(item)
  editedItem.value = Object.assign({}, item)
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this deal?')) {
    try {
      await crmService.deleteDeal(item.id)
      await loadDeals()
    } catch (error) {
      console.error('Failed to delete deal:', error)
    }
  }
}

const close = () => {
  dialog.value = false
  setTimeout(() => {
    editedItem.value = Object.assign({}, defaultItem)
    editedIndex.value = -1
  }, 300)
}

const save = async () => {
  try {
    if (editedIndex.value > -1) {
      await crmService.updateDeal(editedItem.value.id, editedItem.value)
    } else {
      await crmService.createDeal(editedItem.value)
    }
    await loadDeals()
    close()
  } catch (error) {
    console.error('Failed to save deal:', error)
  }
}

const getDealInitials = (title) => {
  if (!title) return '?'
  const words = title.split(' ')
  if (words.length >= 2) {
    return words[0][0] + words[1][0]
  }
  return title.substring(0, 2)
}

const getDealColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo', 'teal', 'orange']
  return colors[index % colors.length]
}
</script>

<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Deals</h1>
            <p class="text-h6 text-grey-darken-1">Track your sales pipeline</p>
          </div>
          <v-btn color="primary" size="large" prepend-icon="mdi-plus" @click="dialog = true" elevation="2">
            Add Deal
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search deals..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn-toggle v-model="viewMode" mandatory variant="outlined" divided density="compact">
                <v-btn value="card" size="small"><v-icon>mdi-view-grid</v-icon></v-btn>
                <v-btn value="table" size="small"><v-icon>mdi-view-list</v-icon></v-btn>
              </v-btn-toggle>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <v-row v-else-if="viewMode === 'card'">
      <v-col v-for="(deal, index) in filteredDeals" :key="deal.id" cols="12" sm="6" md="4" lg="3">
        <v-card elevation="3" class="deal-card h-100" hover>
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar :color="getDealColor(index)" size="48" class="mr-3">
                <span class="text-h6 font-weight-bold text-white">
                  {{ getDealInitials(deal.title) }}
                </span>
              </v-avatar>
              <div class="flex-grow-1">
                <h3 class="text-h6 font-weight-bold text-truncate mb-1">{{ deal.title }}</h3>
                <v-chip :color="getStageColor(deal.stage)" size="x-small" variant="flat" class="text-capitalize font-weight-bold">
                  {{ deal.stage }}
                </v-chip>
              </div>
            </div>

            <v-divider class="my-3"></v-divider>

            <div class="deal-details">
              <div class="d-flex align-center justify-space-between mb-3">
                <span class="text-overline text-grey-darken-1">Deal Value</span>
                <span class="text-h5 font-weight-bold text-green">{{ formatCurrency(deal.amount) }}</span>
              </div>

              <div class="d-flex align-center mb-2" v-if="deal.company_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-office-building</v-icon>
                <span class="text-caption font-weight-medium">{{ deal.company_name }}</span>
              </div>

              <div class="d-flex align-center mb-2" v-if="deal.contact_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-account</v-icon>
                <span class="text-caption">{{ deal.contact_name }}</span>
              </div>

              <div class="d-flex align-center" v-if="deal.expected_close_date">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-calendar</v-icon>
                <span class="text-caption">{{ formatDate(deal.expected_close_date) }}</span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="pa-3 pt-0">
            <v-btn size="small" variant="text" color="primary" prepend-icon="mdi-pencil" @click="editItem(deal)">
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn size="small" variant="text" color="error" icon="mdi-delete" @click="deleteItem(deal)"></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="filteredDeals.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-handshake-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No deals found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first deal' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-plus">Add Deal</v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table :headers="headers" :items="filteredDeals" :loading="loading" items-per-page="15">
            <template v-slot:item.title="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getDealColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getDealInitials(item.title) }}
                  </span>
                </v-avatar>
                <span class="font-weight-medium">{{ item.title }}</span>
              </div>
            </template>
            <template v-slot:item.amount="{ item }">
              <span class="font-weight-bold text-green">{{ formatCurrency(item.amount) }}</span>
            </template>
            <template v-slot:item.stage="{ item }">
              <v-chip :color="getStageColor(item.stage)" size="small" variant="flat" class="text-capitalize font-weight-bold">
                {{ item.stage }}
              </v-chip>
            </template>
            <template v-slot:item.company_name="{ item }">
              <v-chip v-if="item.company_name" size="small" variant="tonal" prepend-icon="mdi-office-building">
                {{ item.company_name }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.contact_name="{ item }">
              <v-chip v-if="item.contact_name" size="small" variant="tonal" prepend-icon="mdi-account">
                {{ item.contact_name }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.expected_close_date="{ item }">
              <span v-if="item.expected_close_date">{{ formatDate(item.expected_close_date) }}</span>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon size="small" class="mr-2" @click="editItem(item)" color="primary">mdi-pencil</v-icon>
              <v-icon size="small" @click="deleteItem(item)" color="error">mdi-delete</v-icon>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="700px" persistent>
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-4">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">{{ editedIndex === -1 ? 'mdi-handshake-outline' : 'mdi-handshake' }}</v-icon>
            <span class="text-h6 font-weight-bold">{{ editedIndex === -1 ? 'New Deal' : 'Edit Deal' }}</span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.title"
                  label="Deal Title *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedItem.amount"
                  label="Amount *"
                  type="number"
                  prefix="$"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-currency-usd"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.stage"
                  :items="stageOptions"
                  label="Stage *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-chart-timeline-variant"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.company"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Company"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-office-building"
                  clearable
                  hint="Optional: Link this deal to a company"
                  persistent-hint
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.contact"
                  :items="contacts"
                  item-title="email"
                  item-value="id"
                  label="Contact"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-account"
                  clearable
                  hint="Optional: Link this deal to a contact"
                  persistent-hint
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props" :title="`${item.raw.first_name} ${item.raw.last_name}`" :subtitle="item.raw.email"></v-list-item>
                  </template>
                  <template v-slot:selection="{ item }">
                    {{ item.raw.first_name }} {{ item.raw.last_name }}
                  </template>
                </v-select>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.expected_close_date"
                  label="Expected Close Date"
                  type="date"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="close" size="large">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="save" size="large" prepend-icon="mdi-content-save">Save Deal</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.deal-card {
  transition: all 0.3s ease;
  border-top: 4px solid transparent;
}

.deal-card:hover {
  transform: translateY(-4px);
  border-top-color: rgb(var(--v-theme-primary));
}

.deal-details {
  min-height: 120px;
}

.text-navy {
  color: #1a237e;
}
</style>
