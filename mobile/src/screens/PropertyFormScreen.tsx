import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { propertyFormSchema, PropertyFormData } from '../../packages/shared/src/schemas/property';
import { propertiesApi } from '../../packages/shared/src/api/properties';

interface PropertyFormScreenProps {
  navigation: any;
  route: any;
}

export default function PropertyFormScreen({ navigation, route }: PropertyFormScreenProps) {
  const [loading, setLoading] = useState(false);
  const propertyId = route.params?.propertyId;
  const initialData = route.params?.property;

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<PropertyFormData>({
    resolver: zodResolver(propertyFormSchema),
    defaultValues: initialData || {
      property_type: 'single_family',
      bedrooms: 3,
      bathrooms: 2,
      square_feet: 1500,
    },
  });

  const onSubmit = async (data: PropertyFormData) => {
    try {
      setLoading(true);
      
      if (propertyId) {
        await propertiesApi.updateProperty(propertyId, data);
        Alert.alert('Success', 'Property updated successfully');
      } else {
        await propertiesApi.createProperty(data);
        Alert.alert('Success', 'Property created successfully');
      }
      
      navigation.goBack();
    } catch (error) {
      Alert.alert('Error', 'Failed to save property. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>
              {propertyId ? 'Edit Property' : 'Add Property'}
            </Text>
          </View>

          {/* Address Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Property Address</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Street Address</Text>
              <Controller
                control={control}
                name="address"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, errors.address && styles.inputError]}
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                    placeholder="123 Main Street"
                    placeholderTextColor="#9CA3AF"
                  />
                )}
              />
              {errors.address && (
                <Text style={styles.errorText}>{errors.address.message}</Text>
              )}
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, styles.flex1]}>
                <Text style={styles.label}>City</Text>
                <Controller
                  control={control}
                  name="city"
                  render={({ field: { onChange, onBlur, value } }) => (
                    <TextInput
                      style={[styles.input, errors.city && styles.inputError]}
                      onBlur={onBlur}
                      onChangeText={onChange}
                      value={value}
                      placeholder="San Francisco"
                      placeholderTextColor="#9CA3AF"
                    />
                  )}
                />
                {errors.city && (
                  <Text style={styles.errorText}>{errors.city.message}</Text>
                )}
              </View>

              <View style={[styles.inputGroup, { width: 80 }]}>
                <Text style={styles.label}>State</Text>
                <Controller
                  control={control}
                  name="state"
                  render={({ field: { onChange, onBlur, value } }) => (
                    <TextInput
                      style={[styles.input, errors.state && styles.inputError]}
                      onBlur={onBlur}
                      onChangeText={onChange}
                      value={value}
                      placeholder="CA"
                      placeholderTextColor="#9CA3AF"
                      maxLength={2}
                      autoCapitalize="characters"
                    />
                  )}
                />
                {errors.state && (
                  <Text style={styles.errorText}>{errors.state.message}</Text>
                )}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Zip Code</Text>
              <Controller
                control={control}
                name="zip_code"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, errors.zip_code && styles.inputError]}
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                    placeholder="94102"
                    placeholderTextColor="#9CA3AF"
                    keyboardType="numeric"
                  />
                )}
              />
              {errors.zip_code && (
                <Text style={styles.errorText}>{errors.zip_code.message}</Text>
              )}
            </View>
          </View>

          {/* Property Details Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Property Details</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Property Type</Text>
              <Controller
                control={control}
                name="property_type"
                render={({ field: { onChange, value } }) => (
                  <View style={[styles.pickerContainer, errors.property_type && styles.inputError]}>
                    <Picker
                      selectedValue={value}
                      onValueChange={onChange}
                      style={styles.picker}
                    >
                      <Picker.Item label="Single Family" value="single_family" />
                      <Picker.Item label="Condo" value="condo" />
                      <Picker.Item label="Townhouse" value="townhouse" />
                      <Picker.Item label="Multi Family" value="multi_family" />
                      <Picker.Item label="Commercial" value="commercial" />
                      <Picker.Item label="Land" value="land" />
                    </Picker>
                  </View>
                )}
              />
              {errors.property_type && (
                <Text style={styles.errorText}>{errors.property_type.message}</Text>
              )}
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, styles.flex1]}>
                <Text style={styles.label}>Bedrooms</Text>
                <Controller
                  control={control}
                  name="bedrooms"
                  render={({ field: { onChange, onBlur, value } }) => (
                    <TextInput
                      style={[styles.input, errors.bedrooms && styles.inputError]}
                      onBlur={onBlur}
                      onChangeText={(text) => onChange(parseInt(text) || 0)}
                      value={value?.toString()}
                      placeholder="3"
                      placeholderTextColor="#9CA3AF"
                      keyboardType="numeric"
                    />
                  )}
                />
                {errors.bedrooms && (
                  <Text style={styles.errorText}>{errors.bedrooms.message}</Text>
                )}
              </View>

              <View style={[styles.inputGroup, styles.flex1]}>
                <Text style={styles.label}>Bathrooms</Text>
                <Controller
                  control={control}
                  name="bathrooms"
                  render={({ field: { onChange, onBlur, value } }) => (
                    <TextInput
                      style={[styles.input, errors.bathrooms && styles.inputError]}
                      onBlur={onBlur}
                      onChangeText={(text) => onChange(parseFloat(text) || 0)}
                      value={value?.toString()}
                      placeholder="2"
                      placeholderTextColor="#9CA3AF"
                      keyboardType="decimal-pad"
                    />
                  )}
                />
                {errors.bathrooms && (
                  <Text style={styles.errorText}>{errors.bathrooms.message}</Text>
                )}
              </View>

              <View style={[styles.inputGroup, styles.flex1]}>
                <Text style={styles.label}>Sq Ft</Text>
                <Controller
                  control={control}
                  name="square_feet"
                  render={({ field: { onChange, onBlur, value } }) => (
                    <TextInput
                      style={[styles.input, errors.square_feet && styles.inputError]}
                      onBlur={onBlur}
                      onChangeText={(text) => onChange(parseInt(text) || 0)}
                      value={value?.toString()}
                      placeholder="1500"
                      placeholderTextColor="#9CA3AF"
                      keyboardType="numeric"
                    />
                  )}
                />
                {errors.square_feet && (
                  <Text style={styles.errorText}>{errors.square_feet.message}</Text>
                )}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Year Built (Optional)</Text>
              <Controller
                control={control}
                name="year_built"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, errors.year_built && styles.inputError]}
                    onBlur={onBlur}
                    onChangeText={(text) => onChange(text ? parseInt(text) : undefined)}
                    value={value?.toString()}
                    placeholder="1990"
                    placeholderTextColor="#9CA3AF"
                    keyboardType="numeric"
                    maxLength={4}
                  />
                )}
              />
              {errors.year_built && (
                <Text style={styles.errorText}>{errors.year_built.message}</Text>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Notes (Optional)</Text>
              <Controller
                control={control}
                name="notes"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.textArea, errors.notes && styles.inputError]}
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                    placeholder="Additional property notes..."
                    placeholderTextColor="#9CA3AF"
                    multiline
                    numberOfLines={3}
                    textAlignVertical="top"
                  />
                )}
              />
              {errors.notes && (
                <Text style={styles.errorText}>{errors.notes.message}</Text>
              )}
            </View>
          </View>

          {/* Form Actions */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={() => navigation.goBack()}
              disabled={loading}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.submitButton, loading && styles.disabledButton]}
              onPress={handleSubmit(onSubmit)}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.submitButtonText}>
                  {propertyId ? 'Update' : 'Create'} Property
                </Text>
              )}
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 24,
    fontWeight: '600',
    color: '#111827',
  },
  section: {
    backgroundColor: 'white',
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    color: '#111827',
  },
  inputError: {
    borderColor: '#DC2626',
  },
  textArea: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    color: '#111827',
    minHeight: 80,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  flex1: {
    flex: 1,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 12,
    marginTop: 4,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    paddingHorizontal: 16,
    paddingTop: 20,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButton: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  submitButton: {
    backgroundColor: '#2563EB',
  },
  disabledButton: {
    opacity: 0.5,
  },
  cancelButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '500',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
});