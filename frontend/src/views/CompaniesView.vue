<script setup>
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { crmService } from '../services/api'

const route = useRoute()
const companies = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card') // 'card' or 'table'
const search = ref('')
const editedIndex = ref(-1)
const editedItem = ref({
  name: '',
  industry: '',
  website: '',
  phone: '',
  email: '',
  address: ''
})

const defaultItem = {
  name: '',
  industry: '',
  website: '',
  phone: '',
  email: '',
  address: ''
}

const headers = [
  { title: 'Company', key: 'name', sortable: true },
  { title: 'Industry', key: 'industry', sortable: true },
  { title: 'Email', key: 'email', sortable: false },
  { title: 'Phone', key: 'phone', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

const filteredCompanies = computed(() => {
  if (!search.value) return companies.value
  const searchLower = search.value.toLowerCase()
  return companies.value.filter(company =>
    company.name?.toLowerCase().includes(searchLower) ||
    company.industry?.toLowerCase().includes(searchLower) ||
    company.email?.toLowerCase().includes(searchLower)
  )
})

onMounted(async () => {
  await loadCompanies()
})

onActivated(async () => {
  await loadCompanies()
})

const loadCompanies = async () => {
  loading.value = true
  try {
    const response = await crmService.getCompanies()
    companies.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load companies:', error)
  } finally {
    loading.value = false
  }
}

const editItem = (item) => {
  editedIndex.value = companies.value.indexOf(item)
  editedItem.value = Object.assign({}, item)
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this company?')) {
    try {
      await crmService.deleteCompany(item.id)
      await loadCompanies()
    } catch (error) {
      console.error('Failed to delete company:', error)
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
      await crmService.updateCompany(editedItem.value.id, editedItem.value)
    } else {
      await crmService.createCompany(editedItem.value)
    }
    await loadCompanies()
    close()
  } catch (error) {
    console.error('Failed to save company:', error)
  }
}

const getCompanyInitials = (name) => {
  if (!name) return '?'
  const words = name.split(' ')
  if (words.length >= 2) {
    return words[0][0] + words[1][0]
  }
  return name.substring(0, 2)
}

const getCompanyColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo']
  return colors[index % colors.length]
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Companies</h1>
            <p class="text-h6 text-grey-darken-1">Manage your business relationships</p>
          </div>
          <v-btn
            color="primary"
            size="large"
            prepend-icon="mdi-plus"
            @click="dialog = true"
            elevation="2"
          >
            Add Company
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Toolbar -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search companies..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
              
              <v-spacer></v-spacer>
              
              <v-btn-toggle
                v-model="viewMode"
                mandatory
                variant="outlined"
                divided
                density="compact"
              >
                <v-btn value="card" size="small">
                  <v-icon>mdi-view-grid</v-icon>
                </v-btn>
                <v-btn value="table" size="small">
                  <v-icon>mdi-view-list</v-icon>
                </v-btn>
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

    <!-- Card View -->
    <v-row v-else-if="viewMode === 'card'">
      <v-col
        v-for="(company, index) in filteredCompanies"
        :key="company.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card elevation="3" class="company-card h-100" hover>
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar
                :color="getCompanyColor(index)"
                size="48"
                class="mr-3"
              >
                <span class="text-h6 font-weight-bold text-white">
                  {{ getCompanyInitials(company.name) }}
                </span>
              </v-avatar>
              <div class="flex-grow-1">
                <h3 class="text-h6 font-weight-bold text-truncate">{{ company.name }}</h3>
                <p class="text-caption text-grey text-truncate">{{ company.industry || 'No industry' }}</p>
              </div>
            </div>

            <v-divider class="my-3"></v-divider>

            <div class="company-details">
              <div class="d-flex align-center mb-2" v-if="company.email">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-email</v-icon>
                <span class="text-caption text-truncate">{{ company.email }}</span>
              </div>
              <div class="d-flex align-center mb-2" v-if="company.phone">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-phone</v-icon>
                <span class="text-caption">{{ company.phone }}</span>
              </div>
              <div class="d-flex align-center" v-if="company.website">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-web</v-icon>
                <a :href="company.website" target="_blank" class="text-caption text-primary text-truncate">
                  {{ company.website }}
                </a>
              </div>
            </div>
          </v-card-text>

          <v-card-actions class="pa-3 pt-0">
            <v-btn
              size="small"
              variant="text"
              color="primary"
              prepend-icon="mdi-pencil"
              @click="editItem(company)"
            >
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              size="small"
              variant="text"
              color="error"
              icon="mdi-delete"
              @click="deleteItem(company)"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="filteredCompanies.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-office-building-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No companies found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first company' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-plus">
              Add Company
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Table View -->
    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table
            :headers="headers"
            :items="filteredCompanies"
            :loading="loading"
            items-per-page="15"
          >
            <template v-slot:item.name="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getCompanyColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getCompanyInitials(item.name) }}
                  </span>
                </v-avatar>
                <span class="font-weight-medium">{{ item.name }}</span>
              </div>
            </template>
            <template v-slot:item.industry="{ item }">
              <v-chip v-if="item.industry" size="small" variant="tonal">
                {{ item.industry }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.email="{ item }">
              <span v-if="item.email">{{ item.email }}</span>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.phone="{ item }">
              <span v-if="item.phone">{{ item.phone }}</span>
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

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="700px" persistent>
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-4">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">
              {{ editedIndex === -1 ? 'mdi-office-building-plus' : 'mdi-office-building-edit' }}
            </v-icon>
            <span class="text-h6 font-weight-bold">
              {{ editedIndex === -1 ? 'New Company' : 'Edit Company' }}
            </span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.name"
                  label="Company Name *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-office-building"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.industry"
                  label="Industry"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-domain"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.email"
                  label="Email"
                  type="email"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-email"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.phone"
                  label="Phone"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-phone"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.website"
                  label="Website"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-web"
                  placeholder="https://example.com"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.address"
                  label="Address"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-map-marker"
                  rows="3"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="close" size="large">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="save" size="large" prepend-icon="mdi-content-save">
            Save Company
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.company-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.company-card:hover {
  transform: translateY(-4px);
  border-left-color: rgb(var(--v-theme-primary));
}

.company-details {
  min-height: 72px;
}

.text-navy {
  color: #1a237e;
}
</style>
