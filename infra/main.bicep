@description('Primary region for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource naming')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Allowed AKS VM SKU fitting CanadaCentral subscription quota')
param vmSize string = 'Standard_D4ps_v5'

// ==========================================
// 1. NETWORK SECURITY GROUP
// ==========================================
resource nsgAks 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: 'nsg-aks-${location}'
  location: location
  properties: {
    securityRules: [
      {
        name: 'Allow-HTTP-HTTPS'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRanges: [
            '80'
            '443'
          ]
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

// ==========================================
// 2. VIRTUAL NETWORK & SUBNET
// ==========================================
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'vnet-netflex-${location}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.240.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'aks-subnet'
        properties: {
          addressPrefix: '10.240.0.0/22'
          networkSecurityGroup: {
            id: nsgAks.id
          }
        }
      }
    ]
  }
}

// ==========================================
// 3. MANAGED AKS CLUSTER (Free Tier - 4 vCPU Node)
// ==========================================
resource aksCluster 'Microsoft.ContainerService/managedClusters@2024-02-01' = {
  name: 'aks-netflex-origin'
  location: location
  sku: {
    name: 'Base'
    tier: 'Free'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: 'netflex-aks-${uniqueSuffix}'
    agentPoolProfiles: [
      {
        name: 'mainpool'
        count: 1
        vmSize: vmSize
        mode: 'System'
        osType: 'Linux'
        vnetSubnetID: vnet.properties.subnets[0].id
        nodeLabels: {
          workload: 'all-in-one-edge-origin'
        }
      }
    ]
    networkProfile: {
      networkPlugin: 'azure'
      serviceCidr: '10.0.0.0/16'
      dnsServiceIP: '10.0.0.10'
    }
  }
}

// ==========================================
// OUTPUTS
// ==========================================
output aksClusterName string = aksCluster.name
output aksControlPlaneFQDN string = aksCluster.properties.fqdn
