import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Property } from '../../packages/shared/src/types/property';

interface PropertyCardProps {
  property: Property;
  onPress: () => void;
}

export default function PropertyCard({ property, onPress }: PropertyCardProps) {
  const formatPropertyType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      {/* Property Type Badge */}
      <View style={styles.header}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>
            {formatPropertyType(property.property_type)}
          </Text>
        </View>
      </View>

      {/* Address */}
      <Text style={styles.address} numberOfLines={1}>
        {property.address}
      </Text>
      
      <Text style={styles.location}>
        {property.city}, {property.state} {property.zip_code}
      </Text>

      {/* Property Details */}
      <View style={styles.details}>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Beds</Text>
          <Text style={styles.detailValue}>{property.bedrooms}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Baths</Text>
          <Text style={styles.detailValue}>{property.bathrooms}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Sq Ft</Text>
          <Text style={styles.detailValue}>
            {property.square_feet.toLocaleString()}
          </Text>
        </View>
      </View>

      {/* Year Built */}
      {property.year_built && (
        <Text style={styles.yearBuilt}>Built in {property.year_built}</Text>
      )}

      {/* Notes Preview */}
      {property.notes && (
        <Text style={styles.notes} numberOfLines={2}>
          {property.notes}
        </Text>
      )}

      {/* Action Buttons */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Edit</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]}>
          <Text style={[styles.actionButtonText, styles.secondaryButtonText]}>
            Projects
          </Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginVertical: 8,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  badge: {
    backgroundColor: '#DBEAFE',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    color: '#1E40AF',
    fontSize: 12,
    fontWeight: '600',
  },
  address: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  location: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
  },
  details: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E5E7EB',
  },
  detailItem: {
    flex: 1,
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 2,
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  yearBuilt: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  notes: {
    fontSize: 14,
    color: '#4B5563',
    marginTop: 8,
    lineHeight: 20,
  },
  actions: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#EFF6FF',
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#2563EB',
    fontSize: 14,
    fontWeight: '500',
  },
  secondaryButton: {
    backgroundColor: '#F3F4F6',
  },
  secondaryButtonText: {
    color: '#4B5563',
  },
});