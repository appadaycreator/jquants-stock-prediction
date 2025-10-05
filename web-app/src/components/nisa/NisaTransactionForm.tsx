/**
 * 新NISA取引記録フォームコンポーネント
 * 取引の追加・編集を行う
 */

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, Plus, Save, X } from "lucide-react";
import { NisaTransaction, QuotaType, TransactionType } from "@/lib/nisa/types";

interface NisaTransactionFormProps {
  transaction?: NisaTransaction;
  onSubmit: (transaction: Omit<NisaTransaction, "id" | "createdAt" | "updatedAt">) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export default function NisaTransactionForm({ 
  transaction, 
  onSubmit, 
  onCancel, 
  loading = false, 
}: NisaTransactionFormProps) {
  const [formData, setFormData] = useState({
    type: (transaction?.type || "BUY") as TransactionType,
    symbol: transaction?.symbol || "",
    symbolName: transaction?.symbolName || "",
    quantity: transaction?.quantity || 0,
    price: transaction?.price || 0,
    quotaType: (transaction?.quotaType || "GROWTH") as QuotaType,
    transactionDate: transaction?.transactionDate || new Date().toISOString().split("T")[0],
  });

  const [errors, setErrors] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors([]);

    try {
      const amount = formData.quantity * formData.price;
      await onSubmit({
        ...formData,
        amount,
      });
    } catch (error) {
      setErrors([error instanceof Error ? error.message : "Unknown error"]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const amount = formData.quantity * formData.price;

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {transaction ? (
            <>
              <Save className="w-5 h-5" />
              取引記録を編集
            </>
          ) : (
            <>
              <Plus className="w-5 h-5" />
              取引記録を追加
            </>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {errors.length > 0 && (
            <Alert variant="destructive">
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 取引タイプ */}
            <div className="space-y-2">
              <Label htmlFor="type">取引タイプ</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => handleInputChange("type", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="取引タイプを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BUY">買い</SelectItem>
                  <SelectItem value="SELL">売り</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* 投資枠タイプ */}
            <div className="space-y-2">
              <Label htmlFor="quotaType">投資枠</Label>
              <Select
                value={formData.quotaType}
                onValueChange={(value) => handleInputChange("quotaType", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="投資枠を選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GROWTH">成長投資枠</SelectItem>
                  <SelectItem value="ACCUMULATION">つみたて投資枠</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 銘柄コード */}
            <div className="space-y-2">
              <Label htmlFor="symbol">銘柄コード</Label>
              <Input
                id="symbol"
                value={formData.symbol}
                onChange={(e) => handleInputChange("symbol", e.target.value)}
                placeholder="例: 7203"
                required
              />
            </div>

            {/* 銘柄名 */}
            <div className="space-y-2">
              <Label htmlFor="symbolName">銘柄名</Label>
              <Input
                id="symbolName"
                value={formData.symbolName}
                onChange={(e) => handleInputChange("symbolName", e.target.value)}
                placeholder="例: トヨタ自動車"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 数量 */}
            <div className="space-y-2">
              <Label htmlFor="quantity">数量</Label>
              <Input
                id="quantity"
                type="number"
                value={formData.quantity}
                onChange={(e) => handleInputChange("quantity", Number(e.target.value))}
                placeholder="例: 100"
                min="1"
                required
              />
            </div>

            {/* 価格 */}
            <div className="space-y-2">
              <Label htmlFor="price">価格</Label>
              <Input
                id="price"
                type="number"
                value={formData.price}
                onChange={(e) => handleInputChange("price", Number(e.target.value))}
                placeholder="例: 2500"
                min="0"
                step="0.01"
                required
              />
            </div>
          </div>

          {/* 取引日 */}
          <div className="space-y-2">
            <Label>取引日</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {formData.transactionDate ? new Date(formData.transactionDate).toLocaleDateString("ja-JP") : "日付を選択"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={new Date(formData.transactionDate)}
                  onSelect={(date) => {
                    if (date) {
                      handleInputChange("transactionDate", date.toISOString().split("T")[0]);
                    }
                  }}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* 取引金額 */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">取引金額</span>
              <span className="text-lg font-semibold">
                ¥{amount.toLocaleString()}
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {formData.quantity}株 × ¥{formData.price.toLocaleString()} = ¥{amount.toLocaleString()}
            </div>
          </div>

          {/* ボタン */}
          <div className="flex gap-3 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              <X className="w-4 h-4 mr-2" />
              キャンセル
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || loading}
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  保存中...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {transaction ? "更新" : "追加"}
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
