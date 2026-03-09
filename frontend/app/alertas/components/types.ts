export interface AlertFilters {
  setor: string;
  ufs: string[];
  valor_min: number | null;
  valor_max: number | null;
  keywords: string[];
}

export interface Alert {
  id: string;
  name: string;
  filters: AlertFilters;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertFormData {
  name: string;
  setor: string;
  ufs: string[];
  valor_min: string;
  valor_max: string;
  keywords: string[];
}

export const EMPTY_FORM: AlertFormData = {
  name: "",
  setor: "",
  ufs: [],
  valor_min: "",
  valor_max: "",
  keywords: [],
};
