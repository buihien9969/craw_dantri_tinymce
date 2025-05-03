<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('writing_guidelines', function (Blueprint $table) {
            $table->id('guideline_id');
            $table->string('category', 50); // Loại tiêu chí (content, seo, image, etc)
            $table->string('name', 255); // Tên tiêu chí
            $table->text('description'); // Mô tả chi tiết
            $table->text('requirements')->nullable(); // Yêu cầu cụ thể
            $table->boolean('is_required')->default(false); // Bắt buộc hay không
            $table->json('validation_rules')->nullable(); // Quy tắc kiểm tra
            $table->integer('order')->default(0); // Thứ tự hiển thị
            $table->boolean('is_active')->default(true); // Trạng thái
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('writing_guidelines');
    }
};
